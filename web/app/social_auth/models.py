# -*- coding: utf8 -*-
from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
from datetime import timedelta

from social_auth.managers import SocialAuthManager

import pytz

class Manager(User):

    NETWORK_CHOICES =  (
        ('vk', 'vk.com'),
        ('fb', 'facebook.com')
    )

    class Meta:
        unique_together = (('uid', 'network'),)

    uid = models.IntegerField(blank=False)
    network = models.CharField(max_length=2, blank=False, choices=NETWORK_CHOICES)

    access_token = models.CharField(max_length=256, default='')
    code = models.CharField(max_length=256, default='')
    expires_in = models.DateTimeField(null=True)

    objects = SocialAuthManager()

    def is_token_valid(self):
        """ Возвращает True, если токен действителен """
        if self.expires_in is None:
            return False

        return datetime.utcnow().replace(tzinfo=pytz.utc) + \
                timedelta(seconds=-60) < self.expires_in

    def set_access_token(self, access_token, expires_in):
        """ Сохранить токен доступа """
        
        # записать данные
        self.access_token = access_token
        try:
            self.expires_in = datetime.utcnow().replace(tzinfo=pytz.utc) + \
                                timedelta(seconds=int(expires_in))
        except ValueError:
            return

        # Сохранить в базу данных
        self.save()

    def get_access_token(self):
        """ Возвращает действительный токен доступа """

        if not self.is_token_valid():
            return None

        return self.access_token

    def kv_read(self, key):
        """ Возвращает значение ключа для текущего менеджера """

        try:
            return KeyValue.objects.get(manager=self, key=key).value
        except:
            return None        

    def kv_write(self, key, value=''):
        """ Записывает новое значение для ключа """

        kv, created = KeyValue.objects.get_or_create(manager=self, key=key[:128])
        kv.value = value[:8092]
        kv.save()


    def __unicode__(self):
        return u'%s@%s' % (self.uid, self.network)

class KeyValue(models.Model):
    
    """ Таблица """

    class Meta:
        unique_together = (('manager', 'key'), )

    manager = models.ForeignKey(Manager)
    key = models.CharField(max_length=128, db_index=True)
    value = models.CharField(max_length=8092)

class Login(models.Model):

    manager = models.ForeignKey(Manager)
    timestamp = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=15, db_index=True)
    ua = models.TextField()
