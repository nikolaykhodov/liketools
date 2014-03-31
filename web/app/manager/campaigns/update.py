# -*- coding: utf-8 -*-
from django.db import IntegrityError
from django.http import Http404

from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.helpers import get_all_form_errors
from manager.campaigns.forms import CampaignForm
from manager.models import Campaign
from manager.models import Account
from manager.models import VkPost
from manager.models import VkPostEvent
from manager import helpers

from manager.campaigns.forms import VkPostForm

class UpdateCampaignView(LoginRequiredMixin, BaseView):

    """ Обновить информацию о компании """
    template_name = 'json.html'

    @json_answer
    def post(self, request):

        """ Обновить информацию о компании """

        try:
            campaign = Campaign.objects.get(pk=request.POST.get('campaign_id'), manager=request.user)
        except Campaign.DoesNotExist:
            return {'error': True, 'errors': [u'Неизвестная кампания']}


        form = CampaignForm(request.POST, instance=campaign)
        if not form.is_valid():
            return {'error': True, 'errors': get_all_form_errors(form)}

        form.save(commit=True)

        return {'error': False}


class UpdatePostView(LoginRequiredMixin, BaseView):

    template_name = 'manager/campaigns/add_post_iframe.html'

    def get_context_data(self, **kwargs):

        context = super(UpdatePostView, self).get_context_data(**kwargs)

        # Список аккаунтов пользователя
        context['accounts'] = Account.objects.filter(manager=self.request.user)

        # Пост
        context['post'] = self.post

        # Информация для редактирования диалога
        context['editor_data'] = self.post.editor_data

        context['campaign'] = self.post.campaign

        context['is_updating'] = True

        return context

    def get(self, request, post_id):
        """
        Проверить, что данная кампания принадлежит текущему менеджеру
        """

        try:
            self.post = VkPost.objects.get(campaign__manager=request.user, pk=post_id, status='waiting')
        except VkPost.DoesNotExist:
            raise Http404

        return super(UpdatePostView, self).get(request, post_id)

    @json_answer
    def post(self, request, post_id):
        """
        Обновить данные для поста
        """

        # Найти пост
        try:
            post = VkPost.objects.get(campaign__manager=request.user, pk=post_id, status='waiting')
        except VkPost.DoesNotExist:
            raise Http404

        # Проверить корректность данных
        update_form = VkPostForm(request.user, data=request.POST)

        # Если неправильно, то 
        if not update_form.is_valid():
            # Отправить ответ пользователю
            return dict(
                error = True,
                errors = get_all_form_errors(update_form)
            )

        # Сохранить пост
        update_form.update_post(post)

        # Сформировать сообщение для планировщика
        messages = []
        posting_time, delete_time, message_data = post.get_scheduler_data()

        update_add = None
        try:
            add_event = VkPostEvent.objects.get(post=post, event_type='add').event_id
            action = dict( action="add" )
            action.update(message_data)

            update_add = dict(
                action='update',
                event_id=add_event,
                new_trigger_time=posting_time,
                new_data = message_data
            )
        except (VkPostEvent.DoesNotExist, IntegrityError):
            pass

        update_delete = None
        if delete_time:
            try:
                remove_event = VkPostEvent.objects.get(post=post, event_type='delete').event_id
                action = dict(
                    action="delete",
                    lt_post_id=post.pk,
                    access_token=message_data.get('access_token')
                )

                update_delete = dict(
                    action='update',
                    event_id=remove_event,
                    new_trigger_time=delete_time,
                    new_data=action
                )
            except (VkPostEvent.DoesNotExist, IntegrityError):
                pass

        messages = [update_add, update_delete]

        # Отправить сообщение в планировщик
        helpers.send_to_scheduler(messages)

        return {'error': False}
