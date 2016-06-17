from django.conf.urls import include, url
from django.core import urlresolvers
from django.conf import settings
from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from . import urls
from . import views


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^analytics/', include(urls)),
    ]

@hooks.register('register_admin_menu_item')
def register_styleguide_menu_item():
    return MenuItem(
        _('Analytics'),
        urlresolvers.reverse('wagalytics_dashboard'),
        classnames='icon icon-fa-bar-chart',
        order=1000
    )

@hooks.register('insert_editor_js')
def editor_js():
    return """
        <script>
            (function(w,d,s,g,js,fs){
              g=w.gapi||(w.gapi={});g.analytics={q:[],ready:function(f){this.q.push(f);}};
              js=d.createElement(s);fs=d.getElementsByTagName(s)[0];
              js.src='https://apis.google.com/js/platform.js';
              fs.parentNode.insertBefore(js,fs);js.onload=function(){g.load('analytics');};
            }(window,document,'script'));
        </script>
        <script>
            function fetchGAResults(slug) {
                params = {
                    'ids': '%s',
                    'start-date': 'yesterday',
                    'end-date': 'today',
                    'metrics': 'ga:pageviews',
                    'filters': 'ga:pagePath==' + slug
                }
                apiQuery = gapi.client.analytics.data.ga.get(params)
                apiQuery.execute(handleCoreReportingResults);
            }

            function handleCoreReportingResults(results) {
                if (!results.error) {
                    if (results.rows && results.rows.length)
                        showResults(results.rows[0][0]);
                } else {
                    alert('Something broke: ' + results.message);
                }
            }

            function showResults(yesterday_page_views) {
                html_results = '<li class="object"><h2><label>Analytics</label></h2><fieldset>';
                html_results += 'This page has had <strong>' + yesterday_page_views + '</strong>';
                html_results += ' views in the last 24 hours.</fieldset></li>';
                $('#settings ul[class="objects"]').append(html_results);
            }

            gapi.analytics.ready(function() {
                $.get( "%s", function(data) {
                    gapi.analytics.auth.authorize({
                      'serverAuth': {'access_token': data}
                    });
                    // Work out slug from the 'Live' link. TODO: make less fragile
                    slug = $('a[class="status-tag primary"]').attr('href');
                    fetchGAResults(slug);
                });
            })
        </script>
        """ % (settings.GA_VIEW_ID, reverse('wagalytics_token'))
