# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from main.views import Index, SetTimeZone

urlpatterns = patterns('',
    url(r'^$', Index.as_view(), name='index'),
    url(r'^change_time_zone/$', SetTimeZone.as_view(), name='set_timezone'),
)
