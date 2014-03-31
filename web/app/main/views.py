# -*- coding: utf8 -*-

from django.views.generic.base import TemplateView, View
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

from main.models import Event

from manager.models import Account
from manager.models import VkPost


from datetime import datetime

import pytz

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class SetTimeZone(View):

    def post(self, request):
        request.session['django_timezone'] = pytz.timezone(request.POST['timezone'])
        return redirect(request.META.get('HTTP_REFERER', '/'))

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class BaseView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
         
        local_tz = timezone.get_current_timezone()
        now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)

        context['current_time'] = "%s %s %s %s %s %s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        context['timezones'] = pytz.common_timezones

        return context

class Index(LoginRequiredMixin, BaseView):

    template_name = 'main/index.html'

    def get_context_for_events(self):
        return dict(
            events=Event.objects.all().order_by('-id')
        )

    def get_context_for_posts(self):
        return dict(
            posts=VkPost.objects.all().order_by('-id')
        )

    def get_context_data(self, **kwargs):

        context = super(Index, self).get_context_data(**kwargs)

        tab = self.request.GET.get('tab')
        ext_context = self.get_context_for_events()
        if tab == 'posts':
            ext_context = self.get_context_for_posts()

        context.update(ext_context)

        return context


class AddPost(LoginRequiredMixin, BaseView):

    template_name = 'main/add_post.html'

class AddPostIframe(LoginRequiredMixin, BaseView):

    template_name = 'main/add_post_iframe.html'

    def get_context_data(self, **kwargs):

        context = super(AddPostIframe, self).get_context_data(**kwargs)

        # Список аккаунтов пользователя
        context['accounts'] = Account.objects.filter(manager=self.request.user)

        return context
