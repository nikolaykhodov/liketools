# -*- coding: utf8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from datetime import datetime, timedelta

from manager.models import Account

from main.models import VkPost

import re

class VkPostForm(forms.Form):
    """
    Форма для редактирования/добавления поста. 

    Все ссылки проходят валидацию на существование и возможность чтения.
    """

    posting_account = forms.IntegerField(label=u'Аккаунт')
    
    when_to_post_mode = forms.CharField()
    post_schedule_timestamp = forms.DateTimeField(label=u'Время размещения поста', 
                                                  input_formats=['%d.%m.%Y %H:%M'],
                                                  required=False)

    when_to_delete_mode = forms.CharField()
    delete_schedule_timestamp = forms.DateTimeField(label=u'Время размещения поста', input_formats=['%d.%m.%Y %H:%M'], required=False)

    from_group = forms.BooleanField(label=u'От имени группы?', required=False)

    text = forms.CharField(label=u'Текст сообщения', widget=forms.Textarea(), required=False)
    attachments = forms.CharField(label=u'Приложения', required=False)

    groups = forms.CharField(required=False)

    def __init__(self, manager, *args, **kwargs):
        super(VkPostForm, self).__init__(*args, **kwargs)
        self.manager = manager

    def clean(self):

        text = self.cleaned_data.get('text', '')
        attachments = self.cleaned_data.get('attachments', '')

        if text.strip() == '' and attachments.strip() == '':
            raise ValidationError, u'Должно быть заполнено как минимум одно из полей "Текст сообщения" или "Приложения"'
        
        # ПРоверка режима размещения поста
        when_to_post_mode = self.cleaned_data.get('when_to_post_mode', '')

        if not when_to_post_mode in ['immediately', 'schedule']: # ['immediately', 'interval', 'schedule']
            raise ValidationError, u'Неизвестный режим размещения поста'

        if when_to_post_mode == 'schedule':
            if self.cleaned_data.get('post_schedule_timestamp') is None:
                raise ValidationError, u'Не указано время размещения поста в режиме "По расписанию"'

        # Проверка режима удаления поста
        when_to_delete_mode = self.cleaned_data.get('when_to_delete_mode', '')

        if not when_to_delete_mode in ['no', 'schedule']: #['no', 'after_posting', 'schedule']
            raise ValidationError, u'Неизвестный режим удаления поста'

        if when_to_delete_mode == 'schedule':
            if self.cleaned_data.get('delete_schedule_timestamp') is None:
                raise ValidationError, u'Не указано время удаления поста в режиме "По расписанию"'

        return self.cleaned_data


    def calculate_delete_time(self):
        mode = self.cleaned_data.get('when_to_delete_mode')

        # Режим проверен на этапе очистки данных формы
        if mode == 'no':
            return None
        if mode == 'schedule':
            return self.cleaned_data.get('delete_schedule_timestamp')

    def calculate_post_time(self):
        mode = self.cleaned_data.get('when_to_post_mode')

        # Режим проверен на этапе очистки данных формы
        if mode == 'immediately':
            return datetime.now() + timedelta(minutes=1)
        elif mode == 'schedule':
            return self.cleaned_data.get('post_schedule_timestamp')

    def clean_posting_account(self):
        try:
            account = Account.objects.get(manager=self.manager, pk=self.cleaned_data.get('posting_account'))
        except:
            raise ValidationError, u'Неизвестный аккаунт'

        if account.access_token == '':
            raise ValidationError, u'Пустой токен доступа у выбранного аккаунта'

        return account

    def clean_attachments(self):
        attachments = self.cleaned_data.get('attachments', '').split(',')
        attachments = filter(lambda x: x != '', attachments)

        return ','.join(attachments)


    def clean_groups(self):
        groups = self.cleaned_data.get('groups', '').split(',')
        groups = filter(lambda gid: re.match(r'^\d+$', gid) is not None, groups)

        if len(groups) == 0:
            raise ValidationError, u'Нет ни одного валидного номера группы'

        return map(lambda gid: int(gid), groups)

    def process(self):
        posts = []

        post_time = self.calculate_post_time()
        delete_time = self.calculate_delete_time()

        for gid in self.cleaned_data['groups']:
            posts.append(VkPost.objects.create(
                owner_id=-gid,
                from_group=True,

                when_to_post=post_time,
                when_to_delete=delete_time,

                access_token=self.cleaned_data['posting_account'].access_token,
                text=self.cleaned_data['text'].encode('utf8'),
                attachments=self.cleaned_data['attachments']
            ))

        return posts




