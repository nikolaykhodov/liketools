# -*- coding: utf8 -*-

from django.contrib import admin
from social_auth.models import Login, Manager

class LoginAdmin(admin.ModelAdmin):
    list_display = ('manager', 'timestamp', 'ip', 'ua')

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('uid', 'network', )

admin.site.register(Login, LoginAdmin)
admin.site.register(Manager, ManagerAdmin)
