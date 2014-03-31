# -*- coding: utf8 -*-

""" Вспомогательные утилиты для манагерского кабинета """

from django.conf import settings
from django.core.urlresolvers import reverse 

from urllib import quote_plus

from manager.vk import API

import re
import pika
import json

def get_auth_url():
    """ Возвращает URL для аутентификации в соц. сети """
    return "https://oauth.vk.com/authorize?client_id=%s&scope=groups,photos,audio,video&redirect_uri=%s&response_type=code" % (
        settings.APP_ID,
        quote_plus(settings.SOCIAL_AUTH_HOST + reverse('social_auth_vk'))
    )

def get_admin_groups(token):
    """
    Возвращает массив групп, где пользователь с токеном token - администратор

    Параметры:
        -- token - токен доступа
    """

    # Запросить список групп
    api = API(token)
    groups = api.groups.get(count=1000, extended=1)[1:]

    # Выбрать группы
    gids = []
    for group in groups:
        if group.get('is_admin', False) == 1:
            gids.append(group)

    return gids


def get_access_token(token):
    """ 
    Возвращает токен 

    Параметры:
        -- token - токен или ссылка с токеном
    """
    
    # Попробовать вытащить токен из URL
    matches = re.findall(r'access_token=([0-9a-f]+)', token)
    if len(matches) == 1:
        return matches[0]

    # Или вернуть саму строку: это токен
    return token

def get_all_form_errors(form):
    """
    Возвращает список всех ошибок в форме в одном массиве

    Параметры:
        -- form - форма
    """

    # Объединить все ошибки в один массив
    errors = []
    for field in form.errors.keys():
        for error in form.errors[field]:
            if field == '__all__':
                field_name = ''
            else:
                if form.fields[field].label:
                    field_name = form.fields[field].label
                else:
                    field_name = field

                field_name = field_name + ': '

            errors.append(
                '%s%s' % (field_name, error)
            )

    return errors


def send_to_queue(queue, messages):
    """

    Посылает сообщения в заданную очередь

    Параметры:
        -- queue - название очереди
        -- messages - массив сообщений 
    """
    
    if not isinstance(messages, list):
        messages = [messages]

    connection = pika.BlockingConnection(pika.ConnectionParameters( host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.SCHEDULER_QUEUE, durable=True)
    for message in messages:
        channel.basic_publish(exchange='', 
                                routing_key=queue,
                                body=json.dumps(message),  
                                properties=pika.BasicProperties(
                                    delivery_mode = 2, # make message persistent
                               ))
    connection.close()

def send_to_scheduler(messages):
    """
    Send message about posting 
    """

    send_to_queue(settings.SCHEDULER_QUEUE, messages)
