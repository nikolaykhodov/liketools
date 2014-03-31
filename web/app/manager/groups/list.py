# -*- coding: utf8 -*-
from main.views import BaseView
from main.views import LoginRequiredMixin
from manager.models import Group

class ListGroupsView(LoginRequiredMixin, BaseView):

    template_name = 'manager/groups/list.html'

    def get_context_data(self, **kwargs):

        context = super(ListGroupsView, self).get_context_data(**kwargs)

        context['groups'] = Group.objects.filter(manager=self.request.user)

        return context

        
    
