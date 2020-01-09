# Wagtail Analytics

(Last Updated 12/17/19 for Wagtail v2.x)

This module provides a simple dashboard of Google Analytics data, integrated into the Wagtail admin UI. Tested on Wagtail 2.0+.

![Screenshot](screenshot.png)

![Screenshot](wagalytics-page-stats.png)

## Instructions

1. [Create a service account](https://ga-dev-tools.appspot.com/embed-api/server-side-authorization) and download the JSON key (Credentials > Create Credentials > API key)
1. Make sure the [Analytics API is enabled for your project](https://console.developers.google.com/apis/api/analytics.googleapis.com) (See [issue 2](https://github.com/tomdyson/wagalytics/issues/2))
1. Add the [service account email address](https://console.developers.google.com/permissions/serviceaccounts) as a read-only user in Google Analytics (Admin > User Management)
1. Find the ID for your Google Analytics property (Admin > Property > View Settings, note: this is NOT the key that begins with "UA-")
1. Store your JSON key somewhere safe, and do not check it into your repo
1. `pip install wagalytics`
1. Add 'wagalytics' to your INSTALLED_APPS
1. Add 'wagtailfontawesome' to INSTALLED_APPS if it's not there already
1. Update your settings:
 - `GA_KEY_FILEPATH = '/path/to/secure/directory/your-key.json'`

 or when using environment variables (e.g. Heroku):
 - `GA_KEY_CONTENT = 'content_of_your_key.json'`
 - `GA_VIEW_ID = 'ga:xxxxxxxx'`

If you get CryptoUnavailableError errors, you probably need to `pip install PyOpenSSL` and/or `pip install pycrypto`. See [StackOverflow](http://stackoverflow.com/questions/27305867/google-api-access-using-service-account-oauth2client-client-cryptounavailableerr).

Ensure that your code snippet is included on each page you want to be tracked (likely by putting it in your base.html template.) (Admin > Property > Tracking Code)

## Multisite Support

To enable multisite support you'll need to update your Wagalytics settings _and_ have `wagtail.contrib.settings` installed. Sites can use a `GA_KEY_FILEPATH` or a `GA_KEY_CONTENT` key, but it's best not to use both.

In the snippet below, you'll see `site_id`. This is the ID (Primary Key) of your Wagtail Site.
```python
# Use either the GA_KEY_FILEPATH or the GA_KEY_CONTENT setting on your sites,
# but don't use both
WAGALYTICS_SETTINGS = {
    site_id: {
        'GA_VIEW_ID': 'ga:xxxxxxxx',
        'GA_KEY_FILEPATH': '/path/to/secure/directory/your-key.json',
    },
    site_id: {
        'GA_VIEW_ID': 'ga:xxxxxxxx',
        'GA_KEY_CONTENT': 'content_of_your_key.json',
	}
}
```
For every Wagalytics site you add in your multisite `WAGALYTICS_SETTINGS` you'll need to make sure you have the proper GA View ID and API Key. One View ID and API Key won't work for all your sites automatically.

Here's a working example of multisite WAGALYTICS_SETTINGS:

```python
WAGALYTICS_SETTINGS = {
	# My default site. 2 is the site ID. This one uses GA_KEY_FILEPATH.
    2: {
        'GA_VIEW_ID': 'ga:xxxxxxxx',
        'GA_KEY_FILEPATH': '/path/to/secure/directory/your-key.json',
    },
    # The secondary site. 3 is the Site ID. This one uses GA_KEY_CONTENT.
    3: {
        'GA_KEY_CONTENT': 'content_of_your_key.json',
        'GA_VIEW_ID': 'ga:xxxxxxxx',
    }
}
```

## Wagalytics Developers

Developers will need to carry out the following steps after cloning wagalytics:

- Ensure NodeJS & NPM are installed
- Run `npm install` then `npm run build` in the top level wagalytics directory

You will need to run `npm run build` anytime the javascript source is updated.

### TODO

 - [ ] allow configuration of results
 - [x] better styling, e.g. using [chart.js](https://ga-dev-tools.appspot.com/embed-api/third-party-visualizations/)
 - [ ] Throw an error if the relevant settings aren't available
 - [x] add [per-page results](https://github.com/tomdyson/wagalytics/issues/12)

### Notes

This module doesn't help with recording user activity. See [the Wagtail docs](http://docs.wagtail.io/en/latest/topics/writing_templates.html?highlight=analytics#varying-output-between-preview-and-live) and [StackOverflow](http://stackoverflow.com/a/1272312/181793) for pointers on how to avoid gathering data during preview and testing.

### Contributors

 - Thijs Kramer
 - Stefan Schärmeli
 - Alex Gleason
 - James Ramm
 - Jake Kent
 - Kalob Taulien
