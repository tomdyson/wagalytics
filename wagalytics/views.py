import json
import datetime
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils import timezone
from django.urls import reverse
from collections import OrderedDict
from pyexcel_ods import save_data

from wagtail.contrib.settings.forms import SiteSwitchForm as SettingsSiteSwitchForm
from wagtail.core.models import Site


class SiteSwitchForm(SettingsSiteSwitchForm):
    """Overwrite the get_change_url() method from SiteSwitchForm."""

    @classmethod
    def get_change_url(cls, site, model):
        """Change the url based on the Site."""
        return reverse('wagalytics_site_dashboard', args=[site.pk])


def get_access_token(ga_key_filepath):
    """Get the access token for Google Analytics.

    from https://ga-dev-tools.appspot.com/embed-api/server-side-authorization/
    Defines a method to get an access token from the credentials object.
    The access token is automatically refreshed if it has expired.
    """

    # The scope for the OAuth2 request.
    SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

    # Construct a credentials objects from the key data and OAuth2 scope.
    _credentials = ServiceAccountCredentials.from_json_keyfile_name(
        ga_key_filepath, SCOPE)

    return _credentials.get_access_token().access_token


def get_access_token_from_str(ga_key_content):
    """Get the access token from a string.

    from https://ga-dev-tools.appspot.com/embed-api/server-side-authorization/
    Defines a method to get an access token from the credentials object.
    The access token is automatically refreshed if it has expired.
    """

    # The scope for the OAuth2 request.
    SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

    # Construct a credentials objects from the key data and OAuth2 scope.
    keyDict = json.loads(ga_key_content.replace('\n', '').replace('\r', ''))
    _credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        keyDict, SCOPE)

    return _credentials.get_access_token().access_token


def token(request, site_id=None):
    """Generate the token.

    Will detect Wagalyics Multisite settings.
    Defaults to single-site settings.
    """

    if hasattr(settings, 'WAGALYTICS_SETTINGS'):
        if site_id is None:
            site_id = request.site.id

        wagalytics_settings = settings.WAGALYTICS_SETTINGS[site_id]

        if wagalytics_settings.get('GA_KEY_CONTENT', None):
            access_token = get_access_token_from_str(wagalytics_settings['GA_KEY_CONTENT'])
        elif wagalytics_settings.get('GA_KEY_FILEPATH', None):
            access_token = get_access_token(wagalytics_settings['GA_KEY_FILEPATH'])
        else:
            return HttpResponseForbidden()
    else:
        if (hasattr(settings, 'GA_KEY_CONTENT') and settings.GA_KEY_CONTENT != ''):
            access_token = get_access_token_from_str(settings.GA_KEY_CONTENT)
        elif (hasattr(settings, 'GA_KEY_FILEPATH') and settings.GA_KEY_FILEPATH != ''):
            access_token = get_access_token(settings.GA_KEY_FILEPATH)
        else:
            return HttpResponseForbidden()

    return HttpResponse(access_token)


def dashboard(request, site_id=None):
    """Display the Wagalytics Dashboard.

    If a site_id is provided, the dashboard will display an instance of a multi site.
    """
    # If there is no site_id provided in the URL but WAGALYTICS_SETTINGS have been set,
    # Redirect the viewer to the site main site.
    # Default redirect will be to the current site they are. ie. ^analytics/dashboard/2/$
    if not site_id and (hasattr(settings, 'WAGALYTICS_SETTINGS') and len(settings.WAGALYTICS_SETTINGS) > 0):
        # This site has multi-site wagalytics enabled.
        # Redirect user to ^analytics/dashboard/{site_id}/$
        return redirect('wagalytics_site_dashboard', site_id=request.site.id)

    initial_start_date = (timezone.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    ga_view_id = None

    if site_id:
        # Multisite analytics URL is being used.
        # The URL being used looks something like this: ^/analytics/dashboard/2/$

        # Look for the site object, or 404.
        site = get_object_or_404(Site, id=site_id)

        # Check for wagtail.contrib.settings app. Without it, the SiteSwitcher is not available.
        if 'wagtail.contrib.settings' not in settings.INSTALLED_APPS:
            display_message = "You must enable the Wagtail Site Settings app for " \
                              "Multisite Wagalytics to work properly."
            messages.error(request, display_message)

        # Check for WAGALYTICS_SETTINGS
        if not hasattr(settings, 'WAGALYTICS_SETTINGS'):
            # Has no WAGALYTICS_SETTINGS at all
            messages.error(request, "You are missing Wagalytics Multisite settings.")
        elif not settings.WAGALYTICS_SETTINGS[site.id]:
            # Has WAGALYTICS_SETTINGS but doesn't have settings for this specific site.
            display_message = "You have Wagalytics Multisite settings, but not " \
                              "for this site. Please add your settings for this site."
            messages.error(request, display_message)
        else:
            # Has WAGALYTICS_SETTINGS for this specific site.
            # Assign WAGALYTICS_SETTINGS[site_id]['GA_VIEW_ID] to ga_view_id for local use
            ga_view_id = settings.WAGALYTICS_SETTINGS[site.id]['GA_VIEW_ID']
    else:
        # The regular ^analytics/dashboard/$ url is being viewed.
        site = Site.objects.get(hostname=request.site.hostname)
        try:
            ga_view_id = settings.GA_VIEW_ID
        except AttributeError:
            display_message = "You are missing your GA_VIEW_ID setting. Your " \
                              "analytics dashboard won't load without this setting."
            messages.error(request, display_message)

        if not hasattr(settings, 'GA_KEY_FILEPATH') and not hasattr(settings, 'GA_KEY_CONTENT'):
            display_message = "You are missing your GA_KEY_FILEPATH or your "\
                              "GA_KEY_CONTENT setting."
            messages.error(request, display_message)

    # Check if a SiteSwitcher is required and add it. Otherwise return None.
    # SiteSwitcher is disabled by default.
    site_switcher = None
    if Site.objects.count() > 1 and hasattr(settings, 'WAGALYTICS_SETTINGS'):
        site_switcher = SiteSwitchForm(site, Site)

    return render(request, 'wagalytics/dashboard.html', {
        'ga_view_id': ga_view_id,
        'initial_start_date': initial_start_date,
        'site_switcher': site_switcher,
        'site_id': site.id,
    })


def export(request):
    """Export the data in the current view."""
    # Get JSON string posted to `data`
    raw_data = request.POST.get('data')

    # Reject a request without data
    if not raw_data:
        return HttpResponseBadRequest()

    # Convert JSON to a Python dict
    data = json.loads(raw_data)

    # Clean up session data
    for n in data["sessions"]:
        # Convert dates into datetime.date objects
        n[0] = datetime.datetime.strptime(n[0], '%Y%m%d').strftime("%Y-%m-%d")
        # Convert session counts into integers
        n[2] = int(n[2])
        # Second key is just the index, which isn't needed
        del n[1]

    # Clean up referrers data
    for n in data["referrers"]:
        # Convert counts into integers
        n[1] = int(n[1])

    # Format spreadsheet file
    ods = OrderedDict()
    ods["Sessions"] = [["Date", "Sessions"]] + data["sessions"]
    ods["Popular Content"] = [["Page URL", "Views"]] + data["pages"]
    ods["Top Referrers"] = [["Source", "Views"]] + data["referrers"]

    # Save the spreadsheet into memory
    io = BytesIO()
    save_data(io, ods)

    # Set response metadata
    response = HttpResponse(content_type='application/vnd.oasis.opendocument.spreadsheet')
    response['Content-Disposition'] = 'attachment; filename="wagalytics.ods"'

    # Write spreadsheet into response
    response.write(io.getvalue())
    return response
