import json
from oauth2client.client import SignedJwtAssertionCredentials
from django.shortcuts import redirect, render
from django.conf import settings


def get_access_token(ga_key_filepath):
    # from https://ga-dev-tools.appspot.com/embed-api/server-side-authorization/
    # Defines a method to get an access token from the credentials object.
    # The access token is automatically refreshed if it has expired.

    # Load the key file's private data.
    with open(ga_key_filepath) as key_file:
        _key_data = json.load(key_file)

    # The scope for the OAuth2 request.
    SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

    # Construct a credentials objects from the key data and OAuth2 scope.
    _credentials = SignedJwtAssertionCredentials(
        _key_data['client_email'], _key_data['private_key'], SCOPE)

    return _credentials.get_access_token().access_token

def dashboard(request):
    return render(request, 'wagalytics/dashboard.html', {
        'access_token': get_access_token(settings.GA_KEY_FILEPATH),
        'ga_view_id': settings.GA_VIEW_ID,
    })
