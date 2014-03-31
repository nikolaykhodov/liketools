# -*- coding: utf8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse 
from django.test.client import Client

from social_auth.models import Manager

import json

class ManagerTest(TestCase):

    def test_readwrite(self):
        """ 
        
        """
        
        manager = Manager.objects.create_user(uid=1, network='vk')
        manager.kv_write('key1', 'val1')
        manager.kv_write(u'Ключ1', 'val2')

        self.assertEqual(manager.kv_read('key1'), 'val1')
        self.assertEqual(manager.kv_read(u'Ключ1'), 'val2')
        self.assertEqual(manager.kv_read('key2'), None)

class WebTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

    def test_unauthenticated(self):
        """ Тестирование для неавторизованного пользователя """

        client = Client()
        response = client.post(reverse('keyvalue_set'), {'key1': 'val1'})
        self.assertEqual(response.status_code, 302)

    def test_authenticated(self):

        """ Тестирование для авторизованного пользователя """

        client = Client()
        client.login(uid=1, network='vk')
        response = client.post(reverse('keyvalue_set'), {'key2': 'val1'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], False)
        self.assertEqual(self.manager.kv_read('key2'), 'val1')


