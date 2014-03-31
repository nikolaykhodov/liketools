# -*- coding: utf-8 -*-
from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.campaigns.forms import CampaignForm
from manager.campaigns.forms import VkPostForm
from manager.helpers import get_all_form_errors
from manager.helpers import get_auth_url
from manager import helpers

from manager.models import Account
from manager.models import Campaign

from django.db import IntegrityError
from django.http import Http404

import time
import pytz

class AddCampaignView(LoginRequiredMixin, BaseView):
    
    """ Добавление компании """

    template_name = 'json.html'

    @json_answer
    def post(self, request):

        form = CampaignForm(request.POST, initial={'manager': request.user})
        form.instance.manager = request.user

        if not form.is_valid():
            return {'error': True, 'errors': get_all_form_errors(form)}

        try:
            form.save(commit=True)
        except IntegrityError:
            return {'error': True, 'errors': [u'Такая кампания есть в базе данных']}

        return {'error': False}

class SubmitPostView(LoginRequiredMixin, BaseView):
    
    """ Добавление поста """

    template_name = 'json.html'

    @json_answer
    def post(self, request):
        add_form = VkPostForm(request.user, data=request.POST)

        if add_form.is_valid():
            # сохранить пост в базу данных
            posts = add_form.add_posts()

            # отправить сообщение в планировщик
            for post in posts:
                helpers.send_to_scheduler(dict(
                    action="add",
                    trigger_time=int(time.mktime(post.when_to_post.astimezone(pytz.utc).timetuple())),

                    data=dict(
                        antigate_key=request.POST.get('antigate_key', ''),
                        captcha_attempts=request.POST.get('captcha_attempts', ''),
                        captcha_attempts_delay=request.POST.get('captcha_attempts_delay', ''),
                        posting_delay=request.POST.get('posting_delay', ''),

                        lt_post_id=post.pk,
                        text=post.text,
                        owner_ids=post.owner_ids or "",
                        from_group=post.from_group,
                        attachments=post.attachments,
                        access_token=post.access_token,

                        action="add"
                    )
                ))

                if post.when_to_delete is not None:
                    helpers.send_to_scheduler(dict(
                        action="add",
                        trigger_time=int(time.mktime(post.when_to_delete.astimezone(pytz.utc).timetuple())),

                        data=dict(
                            access_token=post.access_token,
                            lt_post_id=post.pk,
                            action="delete"
                        )
                    ))

            # перенаправить на страницу с таблицей постов
            return {'error': False}
        else:
            # Отправить ответ пользователю
            return dict(
                error = True,
                errors = get_all_form_errors(add_form)
            )

class AddPostView(LoginRequiredMixin, BaseView):

    template_name = 'manager/campaigns/add_post_iframe.html'

    def get_context_data(self, **kwargs):

        context = super(AddPostView, self).get_context_data(**kwargs)

        # Список аккаунтов пользователя
        context['accounts'] = Account.objects.filter(manager=self.request.user)

        # Номер кампании
        context['campaign'] = self.campaign

        # URL для переавторизации
        context['auth_url'] = get_auth_url()

        return context

    def get(self, request, campaign):
        """
        Проверить, что данная кампания принадлежит текущему менеджеру
        """

        try:
            self.campaign = Campaign.objects.get(manager=request.user, pk=campaign)
        except Campaign.DoesNotExist:
            raise Http404

        return super(AddPostView, self).get(request, campaign)
