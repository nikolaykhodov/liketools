# -*- coding: utf8 -*-
from main.views import BaseView
from main.views import LoginRequiredMixin
from main.decorators import json_answer

class UpdateGroupView(LoginRequiredMixin, BaseView):

    template_name = 'manager/groups.html'
