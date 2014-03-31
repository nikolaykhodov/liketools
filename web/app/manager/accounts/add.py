# -*- coding: utf8 -*-
from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.helpers import get_all_form_errors
from manager.accounts.forms import AccountForm

from django.db import IntegrityError

class AddAccountView(LoginRequiredMixin, BaseView):
    
    """ Добавление аккаунта """
    template_name = 'json.html'

    @json_answer
    def post(self, request):
        form = AccountForm(request.POST, initial={'manager': request.user})
        form.instance.manager = request.user

        if not form.is_valid():
            return {'error': True, 'errors': get_all_form_errors(form)}

        # 
        try:
            form.save(commit=True)
        except IntegrityError:
            return {'error': True, 'errors': [u'Такой аккаунт уже есть в базе данных']}

        return {'error': False}

