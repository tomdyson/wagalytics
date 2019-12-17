from __future__ import absolute_import, unicode_literals
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import dashboard, token, export

urlpatterns = [
    path('dashboard/', dashboard, name='wagalytics_dashboard'),
    path('dashboard/<int:site_id>/', dashboard, name='wagalytics_site_dashboard'),
    path('token/', token, name='wagalytics_token'),
    path('token/<int:site_id>/', cache_page(3600)(token), name='wagalytics_site_token'),
    path('export/', export, name='wagalytics_export'),
]
