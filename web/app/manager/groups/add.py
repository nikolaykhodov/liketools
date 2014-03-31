# -*- coding: utf8 -*-
from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.vk import API, APIError
from manager.models import Group

from django.db import IntegrityError

import re

class AddGroupView(LoginRequiredMixin, BaseView):

    template_name = 'json.html'

    @json_answer
    def post(self, request):
        link = self.request.POST.get('link', '')

        matches = re.findall(r'^https?://vk\.com/(.+)', link)
        if len(matches) == 0:
            return {'error': True, 'err_desc': u"Ссылка должна быть в домене ВКонтакте"}

        screen_name = re.sub(r'(public|group|event)', '', matches[0])

        api = API(request.user.get_access_token())
        try:
            answer = api.groups.getById(gid=screen_name)
            
            # Пользователь должен быть админом в группе
            if answer[0]['is_admin'] != 1:
                return {'error': True, 'err_desc': u'Пользователь должны быть администратором в группе'}
        except APIError, e:
            return {'error': True, 'err_desc': "APIError: %s" % e}

        try:
            gid = answer[0]['gid']
            name = answer[0]['name']
        except (KeyError, IndexError):
            return {'error': True, 'err_desc': u'Это не ссылка на группу'}

        try:
            group, created = Group.objects.get_or_create(manager=request.user, gid=gid, name=name, alias=screen_name)
            if not created:
                return {'error': True, 'err_desc': u'Эта группа уже есть в списке'}
        except IntegrityError:
            pass

        return {'error': False}
