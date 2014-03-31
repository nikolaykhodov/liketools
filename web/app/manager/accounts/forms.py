# -*- coding: utf8 -*-

from django import forms

from manager.helpers import get_access_token
from manager.models import Account

class AccountForm(forms.ModelForm):

    """ Форма для редактирования/добавления аккаунтов """

    class Meta:
        model = Account
        fields = ('name', 'access_token')

    def clean_access_token(self):

        access_token = self.cleaned_data.get('access_token', '')

        # Если токен не изменился
        if self.instance and access_token == '':
            return self.instance.access_token

        access_token = get_access_token(access_token)

        if len(access_token) > 128:
            raise forms.ValidationError, u'Длин токена не может превышать 128 символов'

        return access_token
