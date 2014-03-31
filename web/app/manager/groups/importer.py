# -*- coding: utf8 -*-
""" Импорт групп """
from django.db import IntegrityError

from main.views import BaseView
from main.views import LoginRequiredMixin
from main.decorators import json_answer

from manager.helpers import get_admin_groups
from manager.helpers import get_auth_url
from manager.models import Group
from manager.vk import APIError

class ImportGroupsView(LoginRequiredMixin, BaseView):

    """ Импортирвать группы """

    template_name = 'json.html'

    @json_answer
    def post(self, request):
        """ POST """

        # Получить токен
        token = request.user.get_access_token()

        # Получить список групп, где пользователь админ
        try:
            groups = get_admin_groups(token)
        except APIError, ex:
            return {'error': True, 'err_desc': u'%s' % ex}

        for group in groups:
            try:
                Group.objects.get_or_create(manager=request.user, gid=group.get('gid'), name=group.get('name', ''), alias=group.get('screen_name', ''))
            except IntegrityError:
                pass
        return {'error': False}    

class GetCountGroupsView(LoginRequiredMixin, BaseView):

    """ Получить список групп пользователя, где он администратор """

    template_name = 'json.html'

    @json_answer
    def post(self, request):
        """ POST """

        # Получить токен
        token = request.user.get_access_token()

        try:
            groups = get_admin_groups(token)
        except APIError, ex:
            desc = u'%s' % ex

            # Добавить URL для переавторизации в случае отзыва или истечения
            # срока действия токена
            auth_url = ''
            if desc.find('revoke') >= 0 or desc.find('expire') >= 0:
                auth_url = get_auth_url()

            return {'error': True, 'err_desc': u'%s' % ex, 'auth_url': auth_url}

        return {'error': False, 'count': len(groups)}
