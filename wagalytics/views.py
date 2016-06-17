import json
from oauth2client.service_account import ServiceAccountCredentials
from django.shortcuts import redirect, render
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

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

@cache_page(3600)
def token(request):
    # return a cached access token to ajax clients
    access_token = get_access_token(settings.GA_KEY_FILEPATH)
    return HttpResponse(access_token)

def dashboard(request):
    return render(request, 'wagalytics/dashboard.html', {
        'ga_view_id': settings.GA_VIEW_ID,
    })
