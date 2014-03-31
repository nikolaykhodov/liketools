# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from manager.views import AddGroupView, UpdateGroupView, DeleteGroupView, ListGroupsView
from manager.views import ImportGroupsView, GetCountGroupsView
from manager.views import Options
from manager.views import AddAccountView, CheckAccountView, DeleteAccountView, ListAccountsView, UpdateAccountView
from manager.views import AddCampaignView, DeleteCampaignView, UpdateCampaignView, ListCampaignsView
from manager.views import AddPostView, DeletePostView, UpdatePostView, ListPostsView, SubmitPostView

urlpatterns = patterns('',
    url(r'^options/$', Options.as_view(), name='manager_options'),

    url(r'^groups/$', ListGroupsView.as_view(), name='manager_groups_list'),
    url(r'^groups/update/$', UpdateGroupView.as_view(), name='manager_group_update'),
    url(r'^groups/add/$', AddGroupView.as_view(), name='manager_group_add'),
    url(r'^groups/delete/$', DeleteGroupView.as_view(), name='manager_group_delete'),

    url(r'^groups/import/$', ImportGroupsView.as_view(), name='manager_import_groups'),
    url(r'^groups/import/count/$', GetCountGroupsView.as_view(), name='manager_import_get_count'),

    url(r'^accounts/$', ListAccountsView.as_view(), name='manager_accounts_list'),
    url(r'^accounts/add/$', AddAccountView.as_view(), name='manager_account_add'),
    url(r'^accounts/check/$', CheckAccountView.as_view(), name='manager_account_check'),
    url(r'^accounts/delete/$', DeleteAccountView.as_view(), name='manager_account_delete'),
    url(r'^accounts/update/$', UpdateAccountView.as_view(), name='manager_account_update'),


    url(r'^campaigns/$', ListCampaignsView.as_view(), name='manager_campaigns_list'),
    url(r'^campaigns/add/$', AddCampaignView.as_view(), name='manager_campaign_add'),
    url(r'^campaigns/update/$', UpdateCampaignView.as_view(), name='manager_campaign_update'),
    url(r'^campaigns/delete/$', DeleteCampaignView.as_view(), name='manager_campaign_delete'),

    url(r'^posts/(?P<campaign>\d+)/', ListPostsView.as_view(), name='manager_posts_list'),
    url(r'^posts/submit/$', SubmitPostView.as_view(), name='manager_post_submit'),
    url(r'^posts/add/(?P<campaign>\d+)/$', AddPostView.as_view(), name='manager_post_add'),
    url(r'^posts/update/(?P<post_id>\d+)/$', UpdatePostView.as_view(), name='manager_post_update'),
    url(r'^posts/delete/$', DeletePostView.as_view(), name='manager_post_delete'),

)
