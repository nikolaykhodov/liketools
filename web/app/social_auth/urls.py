# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from social_auth.views import VkAuthView, LoginView, LogoutView, KvSetView

urlpatterns = patterns('',
    url(r'^login/$', LoginView.as_view(), name='social_auth_login'),
    url(r'^logout/$', LogoutView.as_view(), name='social_auth_logout'),
    url(r'^vk/$', VkAuthView.as_view(), name='social_auth_vk'),

    url(r'^keyvalue_set/$', KvSetView.as_view(), name='keyvalue_set'),
)
