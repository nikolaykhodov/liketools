# -*- coding: utf8 -*-
from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.models import Account

class DeleteAccountView(LoginRequiredMixin, BaseView):

    """ Удаление аккаунтов """

    template_name = 'json.html'

    @json_answer
    def post(self, request):
        ids = request.POST.getlist('ids[]')
        Account.objects.filter(manager=request.user).filter(id__in=ids).delete()

        return {'error': False}

