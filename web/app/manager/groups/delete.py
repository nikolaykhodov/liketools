# -*- coding: utf8 -*-
from main.views import BaseView
from main.views import LoginRequiredMixin
from main.decorators import json_answer

from manager.models import Group

class DeleteGroupView(LoginRequiredMixin, BaseView):

    """ Удалить выбранные группы """

    template_name = 'json.html'

    @json_answer
    def post(self, request):
        groups = request.POST.getlist('groups[]')
        Group.objects.filter(manager=request.user).filter(gid__in=groups).delete()

        return {'error': False}    
