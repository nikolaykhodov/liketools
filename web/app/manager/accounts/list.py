# -*- coding: utf8 -*-
from django.conf import settings

from main.views import LoginRequiredMixin
from main.views import BaseView
from manager.models import Account


class ListAccountsView(LoginRequiredMixin, BaseView):
    
    """ Выводит список аккаунтов текущего пользователя """

    template_name = 'manager/accounts/list.html'

    def get_context_data(self, **kwargs):

        context = super(ListAccountsView, self).get_context_data(**kwargs)

        context['refresh_token_url'] = 'https://oauth.vk.com/authorize?client_id=%(app_id)s&scope=%(scope)s&redirect_uri=http://oauth.vk.com/blank.html&display=page&response_type=token' % {'app_id': settings.OFFLINE_APP_ID, 'scope': settings.OFFLINE_APP_PERM}
        context['accounts'] = Account.objects.filter(manager=self.request.user)

        return context
