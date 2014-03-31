# -*- coding: utf8 -*-

"""
Вспомогательные функции
"""
from django.conf import settings
from django.core.urlresolvers import reverse 

from urllib import urlencode

import urllib2
import json
import datetime, time


def unix_now(delta_hours=0):
    """
    Возвращает значение времени в UNIX-формате
    Параметры:
        -- delta_hours - смещение от текущего момента в часах
    """
    future = datetime.datetime.now() + datetime.timedelta(minutes=60 * delta_hours)
    return int(time.mktime(future.timetuple()))

def update_token(code):
    """ 
    
    Обновляет токен и возвращает (user_id, access_token, expires_in).
    В случае ошибки возвращает (None, None, None)

    Параметры:
        -- code - авторизационный код
    """

    # URL для валидации кода
    uri = 'https://oauth.vk.com/access_token?' + urlencode(dict(
        client_id=settings.APP_ID,
        client_secret=settings.APP_KEY,
        code=code,
        redirect_uri='http://%s%s' % (settings.SOCIAL_AUTH_HOST, reverse('social_auth_vk'))
    ))

    try:
        answer = json.loads(urllib2.urlopen(uri).read())
        access_token = answer['access_token']
        user_id = answer['user_id']
        expires_in = answer['expires_in']
    except (urllib2.HTTPError, KeyError, ValueError):
        return (None, None, None)

    return (user_id, access_token, expires_in)



