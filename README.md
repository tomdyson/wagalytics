# Wagtail Analytics

This module provides a simple dashboard of Google Analytics data, integrated into the Wagtail admin UI. Tested on Wagtail 1.3.

![Screenshot](screenshot.png)

## Instructions

1. [Create a service account](https://ga-dev-tools.appspot.com/embed-api/server-side-authorization) and download the JSON key
1. Add the [service account email address](https://console.developers.google.com/permissions/serviceaccounts) as a read-only user in Google Analytics (account > property > user management)
1. [Find the ID](https://lucidpress.zendesk.com/hc/en-us/articles/207335356) for your Google Analytics property
1. Store your JSON key somewhere safe
1. `pip install wagalytics`
1. Add 'wagalytics' to your INSTALLED_APPS
1. Add 'wagtailfontawesome' to INSTALLED_APPS if it's not there already
1. Update your settings:
 - `GA_KEY_FILEPATH = '/path/to/secure/directory/your-key.json'`
 - `GA_VIEW_ID = 'ga:xxxxxxxx'`

If you get CryptoUnavailableError errors, you probably need to `pip install PyOpenSSL` and/or `pip install pycrypto`. See [StackOverflow](http://stackoverflow.com/questions/27305867/google-api-access-using-service-account-oauth2client-client-cryptounavailableerr).

### TODO

 - [ ] allow configuration of results
 - [ ] better styling, e.g. using [chart.js](https://ga-dev-tools.appspot.com/embed-api/third-party-visualizations/)
 - [ ] fail gracefully if the relevant settings aren't available
 - [ ] use insert_global_admin_css hook when Wagtail 1.4 is released
 - [ ] add per-page results

### Notes

Per-page results:

```javascript
// https://developers.google.com/analytics/devguides/reporting/core/v3/coreDevguide

function makeApiCall() {
    params = {
        'ids': 'ga:81871816',
        'start-date': 'yesterday',
        'end-date': 'today',
        'metrics': 'ga:pageviews',
        'filters': 'ga:pagePath==/features/'
    }
    apiQuery = gapi.client.analytics.data.ga.get(params)
    apiQuery.execute(handleCoreReportingResults);
}

function handleCoreReportingResults(results) {
    if (!results.error) {
        if (results.rows && results.rows.length)
            console.log(results.rows[0][0]);
    } else {
        alert('Something broke: ' + results.message);
    }
}
```

### Contributors

Thijs Kramer
