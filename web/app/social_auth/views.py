# -*- coding: utf8 -*-

"""
Авторизация пользователя и ограничение доступа
"""

from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse 

from main.views import BaseView
from main.views import LoginRequiredMixin
from main.decorators import json_answer

from social_auth.models import Login
from social_auth.helpers import update_token

def auth_user(request, uid, network):
    """ 
    Авторизует пользователя и возвращает его

    Параметры:
        -- uid - номер пользователя в социальной сети
        -- network - двухбуквенный идентификатор соц. сети (fb или vk)
    """

    # Авторизуем пользователя
    manager = authenticate(uid=uid, network=network)
    login(request, manager)

    # Записываем историю входов
    Login.objects.create(manager=manager, ip=request.META['REMOTE_ADDR'], ua=request.META['HTTP_USER_AGENT']) 


    return manager

class VkAuthView(View):

    """ Авторизация через ВКонтакте """
    
    def get(self, request):

        # Проверить токен
        user_id, access_token, expires_in = update_token(request.GET.get('code', ''))

        if user_id is None:
            return HttpResponseRedirect(reverse('social_auth_login'))

        # Авторизовать пользователя
        manager = auth_user(request, user_id, 'vk')

        # Записать токен
        manager.set_access_token(access_token, expires_in)

        return HttpResponseRedirect('/')

class LoginView(BaseView):

    """ Страница входа """

    template_name = 'social_auth/login.html'

    def get_context_data(self, **kwargs):

        data = super(LoginView, self).get_context_data(**kwargs)

        data['auth_host'] = settings.SOCIAL_AUTH_HOST
        data['app_id'] = settings.APP_ID

        return data
        

class LogoutView(LoginRequiredMixin, BaseView):

    """ Страница выхода """

    template_name = 'social_auth/logout.html'

    def get_context_data(self, **kwargs):


        data = super(LogoutView, self).get_context_data(**kwargs)

        logout(self.request)

        return data

class KvSetView(LoginRequiredMixin, View):

    """ Задание пар значение-ключ """

    @json_answer
    def post(self, request):
        """ Задает значения пар ключ-значение для текущего менеджера """

        manager = request.user
        data = request.POST or dict()

        for key in data.keys():
            manager.kv_write(key, data[key])

        return {'error': False}
