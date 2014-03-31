# -*- coding: utf-8 -*-
"""
Класс для доступа к cервисам распознавания, поддерживающих API Антигейта
"""
from base64 import b64encode
from urllib2 import HTTPError
from urllib import urlencode
import re
import urllib2
import logging
import settings

import time

class Antigate(object):
    """
    Класс для доступа к сервисам, поддерживающих API antigate.com
    """

    def __init__(self, key, host='antigate.com'):
        """
        Параметры:
            host string - базовый хост сервиса, например, "antigate.com"
            key string -  ключ доступа к сервису
        """
        super(Antigate, self).__init__()

        self.key = key
        self.host = host

    def upload(self, image):
        """
        Upload
        """
        # Подготовить запрос
        post_data = urlencode(dict(
            method='base64',
            key=self.key,
            body=b64encode(image),
            ext='jpg'
        ))
        
        # 
        if settings.DEBUG:
            logging.debug(('http://%s/in.php?' % self.host) + post_data)

        try:
            # Отправить запрос        
            response = urllib2.urlopen('http://%s/in.php' % self.host, post_data).read()
        except HTTPError, ex:
            if settings.DEBUG:
                logging.debug(ex.message)
            raise UnknownError(ex.message)

        # анализ ответа
        matches = re.findall(r'^OK\|(\d+)$', response)

        # Если капча успешно залита
        if len(matches) > 0:
            return matches[0]
        # Нет свободных слотов
        elif response == 'ERROR_NO_SLOT_AVAILABLE':
            raise NoSlotsError
        # Неправильный файл
        elif response in ['ERROR_ZERO_CAPTCHA_FILESIZE', 'ERROR_TOO_BIG_CAPTCHA_FILESIZE', 'ERROR_WRONG_FILE_EXTENSION']:
            raise InvalidFileError
        else:
            raise UnknownError(response) 

        
    def check(self, captcha_id):
        """
        Проверка
        """

        # Подготовить данные для отправки
        get_data = urlencode(dict(
            action='get',
            key=self.key,
            id=captcha_id
        ))

        # 
        if settings.DEBUG:
            logging.debug(('http://%s/in.php?' % self.host) + get_data)

        # Отправить запросы
        try:
            response = urllib2.urlopen(('http://%s/res.php?' % self.host) + get_data).read()
        except HTTPError, ex:
            if settings.DEBUG:
                logging.debug(ex.message)
            raise UnknownError(ex.message)

        # Анализ ответа
        matches = re.findall(r'^OK\|(.*)$', response)

        # Если капча успешно распознана
        if len(matches) > 0:
            return matches[0]
        # Неверный номер капчи
        elif response == 'ERROR_NO_SUCH_CAPCHA_ID':
            raise InvalidCaptchaIDError(captcha_id)
        # Капча еще не готова
        elif response == 'CAPCHA_NOT_READY':
            raise NotReadyError
        # Неизвестная ошибка
        else:
            raise UnknownError(response)

class CaptchaRecognizer(object):

    def __init__(self, antigate_key, wait_time=7, attempts=3, sleep_func=time.sleep):
        
        """

        """

        self.antigate_key = antigate_key
        self.wait_time = wait_time
        self.attempts = attempts
        self.sleep_func = sleep_func

        self.antigate = Antigate(antigate_key)

    def recognize(self, img_url):
        """

        """

        # Скачать картинку

        captcha = urllib2.urlopen(img_url).read()

        # Залить на антигейт и получить номер капчи
        captcha_id = self.antigate.upload(captcha)

        # Делать, столько раз, сколько прописано в self.attempts
        for i in xrange(self.attempts):
            # Проверить, распознана ли капча
            try:
                # Если да, то вернуть ее значение
                return self.antigate.check(captcha_id)
            except NotReadyError:
                pass
            # Иначе ожидать время наступления следующей попытки
            self.sleep_func(self.wait_time)

        raise TimeoutAntigateError


class AntigateError(Exception):
    """
    Ошибки, связанные с сервисами распознования
    """

class NoSlotsError(AntigateError): 
    """
    Нет свобододных слотов для распознавания
    """
    pass

class InvalidFileError(AntigateError): 
    """
    Файл с изображением содержит ошибку
    """
    pass

class UnknownError(AntigateError):
    """
    Неизвестная ошибка
    """

    def __init__(self, response):
        self.response = response

    def __unicode__(self):
        return u'%s' % self.response

class InvalidCaptchaIDError(AntigateError):
    """
    Неверный номер капчи
    """

    pass

class NotReadyError(AntigateError):
    """
    Капча еще не готова
    """

    pass

class TimeoutAntigateError(AntigateError):
    """
    Истекло время ожидания распознавания капчи
    """

    pass
