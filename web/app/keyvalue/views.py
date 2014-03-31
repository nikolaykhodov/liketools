# -*- coding: utf8 -*-
""" View for KeyValue app """

from django.views.generic.base import View
from django.http import HttpResponse

from main.views import LoginRequiredMixin
from keyvalue.models import KeyValue

class SetView(LoginRequiredMixin, View):

    """ Задание пар значение-ключ """

    def post(self, request):
        """ Задает значения пар ключ-значение для текущего менеджера """

        manager = request.user
        data = request.POST or dict()

        for key in data.keys():
            KeyValue.objects.write(manager, key, data[key])

        return HttpResponse('ok')
