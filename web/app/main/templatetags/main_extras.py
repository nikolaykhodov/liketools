# -*- coding: utf8 -*-
from django import template
from django.utils import timezone

import datetime
import json
import re
import pytz

register = template.Library()
@register.filter(name='fromunix')
def fromunix(value):
    dt = datetime.datetime.fromtimestamp(int(value))
    local_tz = timezone.get_current_timezone()
    return dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

@register.filter(name='pretty_json')
def pretty_json(value):
    
    if type(value) == unicode or type(value) == str:
        try:
            obj = json.loads(value)
        except ValueError:
            obj = ''
    else:
        obj = value

    return json.dumps(obj, sort_keys=True, indent=2)

@register.filter(name='mask_by_asterisks')
def mask_by_asterisks(text, number=8):
    
    def replace(match):
        value = match.group(0)
        if len(value) <= number:
            return value
        else:
            pos = (len(value) - number) / 2
            return value[:pos] + '*' * number + value[pos+number:]

    return re.sub(r'[a-z0-9]{16,128}', replace, text)

@register.simple_tag(name='manager_options')
def manager_options(user):
    # Параметры для авторизованного менеджера
    manager_options = {}
    if user.is_authenticated():
        manager = user

        manager_options['antigate_key'] = manager.kv_read('antigate_key') or ''
        manager_options['captcha_attempts'] = manager.kv_read('captcha_attempts') or ''
        manager_options['captcha_attempts_delay'] = manager.kv_read('captcha_attempts_delay') or ''
        manager_options['posting_delay'] = manager.kv_read('posting_delay') or ''
        manager_options['access_token'] = manager.get_access_token() or ''
    
    return json.dumps(manager_options)

@register.filter(name='CSI2List')
def CSI2List(value):
    """
    Преобразует значения поля CommaSeparatedIntegerField в массив чисел
    """
    return json.loads(value)

@register.filter(name='abs')
def template_abs(value):
    """
    Преобразует значения поля CommaSeparatedIntegerField в массив чисел
    """
    return abs(value)


