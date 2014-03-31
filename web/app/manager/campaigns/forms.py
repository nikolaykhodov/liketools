# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError

from manager.models import Account
from manager.models import VkPost
from manager.models import Campaign

from datetime import datetime, timedelta

import re
import pytz
import json

class CampaignForm(forms.ModelForm):
    
    """ Форма для работы с кампаниями """

    class Meta:
        model = Campaign
        fields = ('name',)

    def clean_name(self):

        """ Проверяем уникальность названия кампании """

        name = self.cleaned_data.get('name')
        if Campaign.objects.filter(manager=self.instance.manager, name=name).count() > 0:
            raise forms.ValidationError, u'Такая кампания есть в база данных'

        return name

class VkPostForm(forms.Form):
    """
    Форма для редактирования/добавления поста. 

    Все ссылки проходят валидацию на существование и возможность чтения.
    """

    posting_account = forms.IntegerField(label=u'Аккаунт')

    campaign = forms.IntegerField(label=u'Кампания')
    
    when_to_post_mode = forms.CharField('Режим размещения поста(-ов)')
    post_schedule_timestamp = forms.DateTimeField(label=u'Время размещения поста', 
                                                  input_formats=['%d.%m.%Y %H:%M'],
                                                  required=False)

    when_to_delete_mode = forms.CharField('Режим удаления поста(-ов)')
    delete_schedule_timestamp = forms.DateTimeField(label=u'Время удаления поста', input_formats=['%d.%m.%Y %H:%M'], required=False)

    from_group = forms.BooleanField(label=u'От имени группы?', required=False)

    posting_mode = forms.CharField(label=u'Режим отправки запросов')

    text = forms.CharField(label=u'Текст сообщения', widget=forms.Textarea(), required=False)
    attachments = forms.CharField(label=u'Приложения', required=False)

    groups = forms.CharField(required=False, label=u'Группы')

    editor_data = forms.CharField(required=True, label=u'Данные для редактора постов')

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

        posting_timestamp = None
        if when_to_post_mode == 'schedule':
            posting_timestamp = self.cleaned_data.get('post_schedule_timestamp')
            if posting_timestamp is None:
                raise ValidationError, u'Не указано время размещения поста в режиме "По расписанию"'

            if posting_timestamp < datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(seconds=-60):
                raise ValidationError, u'Время размещения поста - в прошлом'

        # Проверка режима удаления поста
        when_to_delete_mode = self.cleaned_data.get('when_to_delete_mode', '')

        if not when_to_delete_mode in ['no', 'schedule']: #['no', 'after_posting', 'schedule']
            raise ValidationError, u'Неизвестный режим удаления поста'

        if when_to_delete_mode == 'schedule':
            delete_timestamp = self.cleaned_data.get('delete_schedule_timestamp')

            if delete_timestamp is None:
                raise ValidationError, u'Не указано время удаления поста в режиме "По расписанию"'

            # Пост должен быть удален после его размещения
            if posting_timestamp is not None:
                if delete_timestamp < posting_timestamp:
                    raise ValidationError, u'Момент удаления поста - до момента его размещения'

        return self.cleaned_data


    def clean_posting_mode(self):
        """ Проверка режима размещения """

        posting_mode = self.cleaned_data.get('posting_mode', '')
        if not posting_mode in ['one_at_a_time', 'chain']:
            raise ValidationError, u'Неизвестный режим размещения поста(-ов)'

        return posting_mode

    def clean_campaign(self):
        try:
            campaign = Campaign.objects.get(manager=self.manager, pk=self.cleaned_data.get('campaign'))
        except Campaign.DoesNotExist:
            raise ValidationError, u'Неизвестная кампания для данного менеджера'

        return campaign

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

    def clean_editor_data(self):
        editor_data = self.cleaned_data.get('editor_data')
        try:
            editor_data = json.loads(editor_data)
        except ValueError:
            raise ValidationError, u'Информация о состояни редактора должна быть JSON-объектом'

        # В массиве groups должны быть все группы из POST['groups']
        editor_data_groups = editor_data.get('groups', [])
        for group in self.cleaned_data.get('groups', []):
            try:
                if len(filter(lambda x: x.get('gid') == str(group), editor_data_groups)) == 0:
                    raise ValidationError, u'Не все перечисленные группы представлены в списке групп в данных для редактора постов'
            except:
                raise ValidationError, u'Не все перечисленные группы представлены в списке групп в данных для редактора постов'

        return editor_data
    

    def add_posts(self):
        def get_group(data, gid):
            """ Выбирает группу из editor_data по ее номеру """
            for group in data.get('groups', []):
                try:
                    if -int(group.get('gid')) == gid:
                        return group
                except ValueError:
                    pass

            return None

        posts = []

        post_time = self.calculate_post_time()
        delete_time = self.calculate_delete_time()

        # Перевести идентификатор владельца стены в формат ВК
        gids_list = [-gid for gid in self.cleaned_data.get('groups')]

        # При размещении по цепочке, список групп будет для одного поста
        posting_mode = self.cleaned_data.get('posting_mode')
        if posting_mode == 'chain':
            gids_list = [gids_list]

        editor_data = self.cleaned_data.get('editor_data', {})
        for gids in gids_list:

            # Если добавляем по одному, то в JSON-объекте для редактора оставить только одну соответствущую группу
            if posting_mode != 'chain':
                new_editor_data = {}
                new_editor_data.update(editor_data)
                new_editor_data['groups'] = [get_group(editor_data, gids)]
            else:
                new_editor_data = editor_data

            new_editor_data = json.dumps(new_editor_data)
            
            posts.append(VkPost.objects.create(
                campaign=self.cleaned_data['campaign'],
                owner_ids=gids,
                from_group=True,

                when_to_post=post_time,
                when_to_delete=delete_time,

                access_token=self.cleaned_data['posting_account'].access_token,
                text=self.cleaned_data['text'].encode('utf8'),
                attachments=self.cleaned_data['attachments'],
                editor_data=new_editor_data
            ))

        return posts

    def update_post(self, post):

        """ Обновляет пост с новыми данным из формы """

        post_time = self.calculate_post_time()
        delete_time = self.calculate_delete_time()

        # Перевести идентификатор владельца стены в формат ВК
        gids = [-gid for gid in self.cleaned_data.get('groups')]

        post.owner_ids=gids
        post.from_group=True

        post.when_to_post=post_time
        post.when_to_delete=delete_time

        post.access_token=self.cleaned_data['posting_account'].access_token
        post.text=self.cleaned_data['text'].encode('utf8')
        post.attachments=self.cleaned_data['attachments']
        post.editor_data=json.dumps(self.cleaned_data['editor_data'])

        post.save()
