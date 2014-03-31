# -*- coding: utf-8 -*-
from django.http import Http404

from main.views import LoginRequiredMixin
from main.views import BaseView

from manager.models import Campaign
from manager.models import VkPost

class ListCampaignsView(LoginRequiredMixin, BaseView):

    """ Список компаний пользователя """

    template_name = 'manager/campaigns/campaigns_list.html'
    
    def get_context_data(self, **kwargs):

        context = super(ListCampaignsView, self).get_context_data(**kwargs)

        context['campaigns'] = Campaign.objects.filter(manager=self.request.user)

        return context


class ListPostsView(LoginRequiredMixin, BaseView):

    """ Список постов в кампании """

    template_name = 'manager/campaigns/posts_list.html'

    def get_context_data(self, **kwargs):

        context = super(ListPostsView, self).get_context_data(**kwargs)

        try:
            campaign = Campaign.objects.get(manager=self.request.user, pk=kwargs.get('campaign'))
        except:
            raise Http404

        context['posts'] = VkPost.objects.filter(campaign=campaign)
        context['campaign'] = campaign

        return context
