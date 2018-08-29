import json
import datetime
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from django.shortcuts import redirect, render
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from collections import OrderedDict
from pyexcel_ods import save_data

def get_access_token(ga_key_filepath):
    # from https://ga-dev-tools.appspot.com/embed-api/server-side-authorization/
    # Defines a method to get an access token from the credentials object.
    # The access token is automatically refreshed if it has expired.

    # The scope for the OAuth2 request.
    SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

    # Construct a credentials objects from the key data and OAuth2 scope.
    _credentials = ServiceAccountCredentials.from_json_keyfile_name(
        ga_key_filepath, SCOPE)

    return _credentials.get_access_token().access_token

def get_access_token_from_str(ga_key_content):
    # from https://ga-dev-tools.appspot.com/embed-api/server-side-authorization/
    # Defines a method to get an access token from the credentials object.
    # The access token is automatically refreshed if it has expired.

    # The scope for the OAuth2 request.
    SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

    # Construct a credentials objects from the key data and OAuth2 scope.
    keyDict = json.loads(ga_key_content.replace('\n', '').replace('\r', ''))
    _credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        keyDict, SCOPE)

    return _credentials.get_access_token().access_token

@cache_page(3600)
def token(request):
    # return a cached access token to ajax clients
    if (hasattr(settings, 'GA_KEY_CONTENT') and settings.GA_KEY_CONTENT != ''):
        access_token = get_access_token_from_str(settings.GA_KEY_CONTENT)
    else:
        access_token = get_access_token(settings.GA_KEY_FILEPATH)

    return HttpResponse(access_token)

def dashboard(request):
    initial_start_date = (timezone.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    return render(request, 'wagalytics/dashboard.html', {
        'ga_view_id': settings.GA_VIEW_ID,
        'initial_start_date': initial_start_date,
    })

def export(request):
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
