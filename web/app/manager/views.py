# -*- coding: utf8 -*-
from main.views import BaseView
from main.views import LoginRequiredMixin
from manager.groups.add import AddGroupView
from manager.groups.delete import DeleteGroupView
from manager.groups.update import UpdateGroupView
from manager.groups.list import ListGroupsView
from manager.groups.importer import GetCountGroupsView
from manager.groups.importer import ImportGroupsView

from manager.accounts.add import AddAccountView
from manager.accounts.check import CheckAccountView
from manager.accounts.delete import DeleteAccountView
from manager.accounts.list import ListAccountsView
from manager.accounts.update import UpdateAccountView

from manager.campaigns.add import AddCampaignView, AddPostView, SubmitPostView
from manager.campaigns.delete import DeleteCampaignView, DeletePostView
from manager.campaigns.update import UpdateCampaignView, UpdatePostView
from manager.campaigns.list import ListCampaignsView, ListPostsView

class Options(LoginRequiredMixin, BaseView):

    template_name = 'manager/options.html'

    def get_context_data(self, **kwargs):

        manager = self.request.user

        data = super(Options, self).get_context_data(**kwargs)
        data['antigate_key'] = manager.kv_read('antigate_key') or ''
        data['captcha_attempts'] = manager.kv_read('captcha_attempts') or ''
        data['captcha_attempts_delay'] = manager.kv_read('captcha_attempts_delay') or ''
        data['posting_delay'] = manager.kv_read('posting_delay') or ''

        return data
