import pytest

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from wagtail.tests.utils import WagtailTestUtils
from wagtail.core.models import Site
import wagtail_factories

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestWagalyticsDashboard(TestCase, WagtailTestUtils):

    def setUp(self):
        self.dashboard_url = reverse('wagalytics_dashboard')
        # Clear KEY settings in case tests are being run inside of a project.
        self._clean_wagalytics_keys()
        # Login
        self.login()

    def _clean_wagalytics_keys(self):
        """Remove Wagalytics settings."""
        if hasattr(settings, 'WAGALYTICS_SETTINGS'):
            del settings.WAGALYTICS_SETTINGS
        if hasattr(settings, 'GA_VIEW_ID'):
            del settings.GA_VIEW_ID
        if hasattr(settings, 'GA_KEY_FILEPATH'):
            del settings.GA_KEY_FILEPATH
        if hasattr(settings, 'GA_KEY_CONTENT'):
            del settings.GA_KEY_CONTENT

    def _use_single_site_settings(self):
        if hasattr(settings, 'WAGALYTICS_SETTINGS'):
            del settings.WAGALYTICS_SETTINGS

        settings.GA_VIEW_ID = 'ga:xxxxxxxx'
        settings.GA_KEY_FILEPATH = '/path/to/your/analytics-key.json'

    def _use_multi_site_settings(self):
        settings.WAGALYTICS_SETTINGS = {
            # My default site.
            2: {
                'GA_VIEW_ID': 'ga:xxxxxxxx',
                'GA_KEY_FILEPATH': '/path/to/your/analytics-key.json',
            },
            # The secondary site.
            3: {
                'GA_KEY_CONTENT': 'content_of_your_key.json',
                'GA_VIEW_ID': 'ga:xxxxxxxx',
            }
        }


    def test_dashboard_view(self):
        self._use_single_site_settings()
        response_200 = self.client.get(self.dashboard_url)
        # Default URL should not redirect to ^analytics/dashboard/{num}/$
        self.assertEqual(response_200.status_code, 200)

    def test_dashboard_404_view(self):
        response_404 = self.client.get(reverse('wagalytics_site_dashboard', args=(999,)))
        self.assertEqual(response_404.status_code, 404)

    def test_single_site_missing_keys(self):
        self._clean_wagalytics_keys()
        response = self.client.get(self.dashboard_url)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].message, "You are missing your GA_VIEW_ID setting. Your analytics dashboard won't load without this setting.")
        self.assertEqual(messages[1].message, "You are missing your GA_KEY_FILEPATH or your GA_KEY_CONTENT setting.")

    def test_single_site_no_siteswitcher(self):
        """Make sure the site switcher does not show up in the dashboard context."""
        self._clean_wagalytics_keys()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.context['site_switcher'], None)

    def test_single_site_dashboard(self):
        self._use_single_site_settings()
        response = self.client.get(self.dashboard_url)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 0)

    def test_single_site_dashboard_on_multisite_url(self):
        self._use_single_site_settings()
        response = self.client.get(reverse('wagalytics_site_dashboard', args=(2,)))
        self.assertEqual(response.status_code, 200)  # Will still 200.

        messages = list(response.context['messages'])
        # Should have 1 message
        self.assertEqual(len(messages), 1)
        # The one message should be "You are missing Wagalytics Multisite settings."
        self.assertEqual(messages[0].message, "You are missing Wagalytics Multisite settings.")

    def test_multi_site_dashboard(self):
        self._use_multi_site_settings()
        wagtail_factories.SiteFactory(hostname="example.com")
        sites = Site.objects.all()
        # There should be 2 Wagtail Sites.
        self.assertEqual(len(sites), 2)

        # Go to ^analytics/dashboard/{num}/$. Should redirect.
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        # Went to /dashboard/2/ by default
        self.assertEqual(response.url, reverse('wagalytics_site_dashboard', args=(2,)))

    def test_multi_site_siteswitcher(self):
        self._use_multi_site_settings()
        wagtail_factories.SiteFactory(hostname="example.com")

        response = self.client.get(reverse('wagalytics_site_dashboard', args=(2,)))
        self.assertNotEqual(response.context['site_switcher'], None)

    def test_multi_site_dashboard_change_site(self):
        self._use_multi_site_settings()
        wagtail_factories.SiteFactory(hostname="example.com")
        site = Site.objects.last()

        response = self.client.get(reverse('wagalytics_site_dashboard', args=(site.id,)))
        self.assertEqual(response.status_code, 200)

    def test_multi_site_token_no_api_keys(self):
        """Test the ^analytics/token/2/$ url. There will always be an id of 2 available."""
        self._clean_wagalytics_keys()
        url = reverse('wagalytics_site_token', args=(2,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_single_site_token_no_api_keys(self):
        """Test the ^analytics/token/$ url. """
        self._clean_wagalytics_keys()
        url = reverse('wagalytics_token')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_multi_site_token_using_single_site_api_keys(self):
        self._use_single_site_settings()
        url = reverse('wagalytics_site_token', args=(2,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_multi_site_token_using_multi_site_api_keys(self):
        self._use_multi_site_settings()
        url = reverse('wagalytics_site_token', args=(2,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
