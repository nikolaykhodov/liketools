# -*- coding: utf-8 -*-
from main.views import LoginRequiredMixin
from main.views import BaseView
from main.decorators import json_answer

from manager.models import Campaign
from manager import helpers
from manager.models import VkPost

class DeleteCampaignView(LoginRequiredMixin, BaseView):

    """ Удалить посты """

    template_name = 'json.html'

    @json_answer
    def post(self, request):

        """ Удалить посты """

        # Сообщения в планировщик
        messages = []

        ids = request.POST.getlist('ids[]')
        campaigns = Campaign.objects.filter(manager=request.user, pk__in=ids)

        for campaign in campaigns:
            messages.extend(campaign.get_delete_messages())

        # Удалить кампании
        campaigns.delete()

        # Отправить сообщения
        helpers.send_to_scheduler(messages)

        return {'error': False}

class DeletePostView(LoginRequiredMixin, BaseView):

    """ Удаление поста """

    template_name = 'json.html'

    @json_answer
    def post(self, request):

        posts = request.POST.getlist('posts[]')

        # Получить список постов
        posts = VkPost.objects.filter(pk__in=posts).filter(campaign__manager=request.user)

        messages = []
        # Пройтись по всем постам
        for post in posts:
            messages.extend(post.delete())

        # Послать сообщения
        helpers.send_to_scheduler(messages)

        return {'error': False}

