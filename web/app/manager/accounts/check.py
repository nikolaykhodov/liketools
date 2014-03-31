# -*- coding: utf8 -*-
from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.vk import API, APIError
from manager.models import Group

from django.db import IntegrityError


class CheckAccountView(LoginRequiredMixin, BaseView):
    
    """ Проверка валидности аккаунта """
    template_name = 'json.html'
    pass
