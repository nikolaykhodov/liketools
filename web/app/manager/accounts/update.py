# -*- coding: utf8 -*-
from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.helpers import get_all_form_errors
from manager.accounts.forms import AccountForm
from manager.models import Account

class UpdateAccountView(LoginRequiredMixin, BaseView):

    """ Обновление информации об аккаунте """

    template_name = 'json.html'

    @json_answer
    def post(self, request):
        try:
            account = Account.objects.get(manager=request.user, pk=request.POST.get('account_id'))
        except Account.DoesNotExist:
            return {'error': True, 'errors': [u'Неизвестный аккаунт']}

        form = AccountForm(request.POST, instance=account)
        if not form.is_valid():
            return {'error': True, 'errors': get_all_form_errors(form)}

        form.save(commit=True)

        return {'error': False}
