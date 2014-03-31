from django.conf.urls import patterns, include, url
from main.views import Index

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', Index.as_view(), name='index'),

    url(r'^main/', include('main.urls')),
    url(r'^manager/', include('manager.urls')),
    url(r'^social_auth/', include('social_auth.urls')),
    url(r'^keyvalue/', include('keyvalue.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
