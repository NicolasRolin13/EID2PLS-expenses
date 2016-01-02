from django.conf.urls import include, url
from django.contrib import admin

from django.views.i18n import javascript_catalog

urlpatterns = [
    url(r'^admin/jsi18n/$', javascript_catalog),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('expenses.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
