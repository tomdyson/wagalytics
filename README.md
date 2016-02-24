# Wagtail Analytics

This module provides a simple dashboard of Google Analytics data, integrated into the Wagtail admin UI. Tested on Wagtail 1.3.

![Screenshot](screenshot.png)

## Instructions

1. [Create a service account](https://ga-dev-tools.appspot.com/embed-api/server-side-authorization) and download the JSON key
1. Add the service account as a read-only user in Google Analytics
1. [Find the ID](https://lucidpress.zendesk.com/hc/en-us/articles/207335356) for your Google Analytics property
1. Store your JSON key somewhere safe
1. `pip install wagalytics`
1. Add 'wagalytics' to your INSTALLED_APPS.
1. Add 'wagtailfontawesome' to INSTALLED_APPS if it's not there already.
1. Update your settings:
 - `GA_KEY_FILEPATH = '/path/to/secure/directory/your-key.json'`
 - `GA_VIEW_ID = 'ga:xxxxxxxx'`

### TODO

 - [ ] allow configuration of results
 - [ ] better styling, e.g. using [chart.js](https://ga-dev-tools.appspot.com/embed-api/third-party-visualizations/)
 - [ ] fail gracefully if the relevant settings aren't available
