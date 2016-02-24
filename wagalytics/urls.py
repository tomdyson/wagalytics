from __future__ import absolute_import, unicode_literals
from django.conf.urls import url
from wagalytics.views import dashboard

urlpatterns = [
    url(r'^dashboard/$', dashboard, name='wagalytics_dashboard'),
]
