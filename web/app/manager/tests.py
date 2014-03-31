# -*- coding: utf8 -*-
"""
Тестирование манагерского кабинета
"""

from StringIO import StringIO

from django.test import TestCase
from django.core.urlresolvers import reverse 
from django.test.client import Client

from social_auth.models import Manager

from manager.models import Group
from manager.models import Account
from manager.models import Campaign
from manager.helpers import get_access_token

from manager.models import VkPost
from manager.models import VkPostEvent

import mox
import json
import urllib2
import pytz

from manager import helpers
from datetime import datetime
from datetime import timedelta

class AuthTest(TestCase):

    """
    Тестирование запросов от неавторизованных пользователей
    """
    def setUp(self):

        self.group_links = [
            reverse('manager_group_add'),
            reverse('manager_group_delete'),
            reverse('manager_groups_list'),
            reverse('manager_import_groups'),
            reverse('manager_import_get_count'),

            reverse('manager_accounts_list'),
            reverse('manager_account_add'),
            reverse('manager_account_check'),
            reverse('manager_account_update'),

            reverse('manager_campaigns_list'),
            reverse('manager_campaign_add'),
            reverse('manager_campaign_delete'),
            reverse('manager_campaign_update'),

            reverse('manager_groups_list'),
            reverse('manager_group_add'),
            reverse('manager_group_delete'),
            reverse('manager_group_update'),

            reverse('manager_posts_list', args=(1,)),
            reverse('manager_post_submit'),
            reverse('manager_post_add', args=(1,)),
            reverse('manager_post_delete'),
            reverse('manager_post_update', args=(1,))
        ]

        self.client = Client()
        

    def test_unauthenticated(self):
        """
        Проверка редиректов для групп
        """

        # Проверка URL для групп
        for url in self.group_links:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

class ListViewsTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')
        self.campaign = Campaign.objects.create(manager=self.manager, name='test')

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.urls  = [
            reverse('manager_groups_list'),
            reverse('manager_posts_list', args=(self.campaign.pk,)),
            reverse('manager_accounts_list'),
            reverse('manager_post_add', args=(self.campaign.pk,)) # iframe
        ]

    def test_200(self):

        for url in self.urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

class AddGroupTest(TestCase):

    """
    Тестирование добавления групппы
    """

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.anmec_mock = """{"response":[{"gid":43704556,"name":"Anmec.Me","screen_name":"anmec","is_closed":1,"type":"group","photo":"https:\/\/vk.com\/images\/community_50.gif","photo_medium":"https:\/\/vk.com\/images\/community_100.gif","photo_big":"https:\/\/vk.com\/images\/question_a.gif"}]}
        """
        self.durov_mock = """{"error":{"error_code":125,"error_msg":"Invalid group id","request_params":[{"key":"oauth","value":"1"},{"key":"method","value":"groups.getById"},{"key":"gids","value":"durov"}]}}"""

        self.urlopen = urllib2.urlopen
        # Mocking
        self.mox = mox.Mox()
        self.mox.StubOutWithMock(urllib2, 'urlopen')
        urllib2.urlopen('https://api.vk.com/method/groups.getById?', 'access_token=&gid=durov', mox.IgnoreArg()).AndReturn(StringIO(self.durov_mock))
        urllib2.urlopen('https://api.vk.com/method/groups.getById?', 'access_token=&gid=anmec', mox.IgnoreArg()).AndReturn(StringIO(self.anmec_mock))
        self.mox.ReplayAll()

        
    def test_add(self):

        # Добавление простой ссылки
        response = self.client.post(reverse('manager_group_add'), {'link': 'http://vk.com/'})
        self.assertEqual(json.loads(response.content)['error'], True)

        # Добавление негруппы
        response = self.client.post(reverse('manager_group_add'), {'link': 'http://vk.com/durov'})
        self.assertEqual(json.loads(response.content)['error'], True)
        
        # Добавление группы
        response = self.client.post(reverse('manager_group_add'), {'link': 'http://vk.com/anmec'})
        self.assertEqual(json.loads(response.content)['error'], False)
        self.assertEqual(Group.objects.get(manager=self.manager, gid=43704556).alias, "anmec")

        self.mox.VerifyAll()

    def tearDown(self):
        self.mox.UnsetStubs()


class DeleteGroupTest(TestCase):

    """ Тестирование удаления группы """

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')
        
        # Добавляем группы
        Group.objects.create(manager=self.manager, gid=1)
        Group.objects.create(manager=self.manager, gid=2)
        Group.objects.create(manager=self.manager, gid=3)
        Group.objects.create(manager=self.manager, gid=4)
        
        # Клиент
        self.client = Client()
        self.client.login(uid=1, network='vk')

    def test_delete(self):

        self.client.post(reverse('manager_group_delete'), {
            'groups[]': [2, 3]
        })

        self.assertEqual(Group.objects.all().count(), 2)
        self.assertEqual(len(Group.objects.filter(gid__in=[1,4])), 2)

class ImportGroupsTest(TestCase):

    """ Тестирование импорта групп """

    def setUp(self):
        self.groups_mock = """{"response":[4,{"gid":33393308,"name":"Цукерберг позвонит","screen_name":"smmrussia","is_closed":0,"is_admin":0,"is_member":1,"type":"page","photo":"http:\/\/cs419827.userapi.com\/v419827094\/1233\/V2VR6ebZb7k.jpg","photo_medium":"http:\/\/cs419827.userapi.com\/v419827094\/1232\/5gkR3BELVZs.jpg","photo_big":"http:\/\/cs419827.userapi.com\/v419827094\/122d\/3w98DixNgOQ.jpg"},{"gid":47662327,"name":"Тестовое сообщество","screen_name":"club47662327","is_closed":0,"is_admin":1,"is_member":1,"type":"group","photo":"https:\/\/vk.com\/images\/community_50.gif","photo_medium":"https:\/\/vk.com\/images\/community_100.gif","photo_big":"https:\/\/vk.com\/images\/question_a.gif"},{"gid":47662325,"name":"Тестовое сообщество","screen_name":"club47662325","is_closed":0,"is_admin":1,"is_member":1,"type":"group","photo":"https:\/\/vk.com\/images\/community_50.gif","photo_medium":"https:\/\/vk.com\/images\/community_100.gif","photo_big":"https:\/\/vk.com\/images\/question_a.gif"},{"gid":47662332,"name":"Тестовое сообщество","screen_name":"club47662332","is_closed":0,"is_admin":1,"is_member":1,"type":"group","photo":"https:\/\/vk.com\/images\/community_50.gif","photo_medium":"https:\/\/vk.com\/images\/community_100.gif","photo_big":"https:\/\/vk.com\/images\/question_a.gif"}]}"""
        
        self.manager = Manager.objects.create_user(uid=1, network='vk')
        self.manager.access_token = ''
        self.manager.save()

        self.client = Client()
        self.client.login(uid=1, network='vk')

        # Mocking
        self.mox = mox.Mox()
        self.mox.StubOutWithMock(urllib2, 'urlopen')
        urllib2.urlopen('https://api.vk.com/method/groups.get?', 'count=1000&access_token=None&extended=1', mox.IgnoreArg()).InAnyOrder().AndReturn(StringIO(self.groups_mock))
        self.mox.ReplayAll()

    def test_import(self):
        response = self.client.post(reverse('manager_import_groups'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Group.objects.filter(manager=self.manager)), 3)

    def test_count(self):
        response = self.client.post(reverse('manager_import_get_count'))
        self.assertEqual(json.loads(response.content)['count'], 3)
        self.mox.VerifyAll()

    def tearDown(self):
        self.mox.UnsetStubs()
        

class AddAccountTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')
        self.client = Client()
        self.client.login(uid=1, network='vk')


    def test_simple(self):
        """ Простое добавление """
        
        response = self.client.post(reverse('manager_account_add'), {'name': 'test@mail.ru', 'access_token': '08b90e59a5a003'})

        self.assertEqual(Account.objects.get(manager=self.manager, name='test@mail.ru').access_token, '08b90e59a5a003')
        self.assertEqual(response.status_code, 200)

    def test_full_link(self):
        """ Токен содержится в ссылке """

        response = self.client.post(reverse('manager_account_add'), {
            'name': 'test@mail.ru', 
            'access_token': 'https://oauthvk.com/blank.html#access_token=08b90e59a5a003&expires_in=0&user_id=0'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Account.objects.get(manager=self.manager, name='test@mail.ru').access_token, '08b90e59a5a003')

    def test_repeated(self):
        """ Повторное аккаунта с тем же именем """

        response = self.client.post(reverse('manager_account_add'), {'name': 'test@mail.ru', 'access_token': '08b90e59a5a003'})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('manager_account_add'), {'name': 'test@mail.ru', 'access_token': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)
        self.assertEqual(Account.objects.get(manager=self.manager, name='test@mail.ru').access_token, '08b90e59a5a003')

    def test_empty_name(self):
        """ Пустое имя """
        response = self.client.post(reverse('manager_account_add'), {'name': '', 'access_token': '08b90e59a5a003'})
        self.assertEqual(json.loads(response.content)['error'], True)

class DeleteAccountTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.manager2 = Manager.objects.create_user(uid=2, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.id1 = Account.objects.create(manager=self.manager, name='test1', access_token='1').pk
        self.id2 = Account.objects.create(manager=self.manager, name='test2', access_token='3').pk
        self.id3 = Account.objects.create(manager=self.manager2, name='test3', access_token='4').pk

    def test_delete(self):
        """ Сценарий обычного удаления """

        ids = [self.id1, self.id2]
        response = self.client.post(reverse('manager_account_delete'), {
            'ids[]': ids
        })
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Account.objects.filter(manager=self.manager).__len__(), 0)
        self.assertEqual(Account.objects.filter(manager=self.manager2).__len__(), 1)

    def test_anothers_accounts(self):
        """ Удаление чужих аккаунтов """

        response = self.client.post(reverse('manager_account_delete'),{
            'ids[]': [self.id3]
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Account.objects.all().__len__(), 3)

    def tearDown(self):
        self.manager.delete()
        self.manager2.delete()

class UpdateAccountTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.aid = Account.objects.create(manager=self.manager, name='test', access_token='1').pk


    def test_basic(self):
        """ Сценарий обычного обновления """

        response = self.client.post(reverse('manager_account_update'), {
            'account_id': self.aid,
            'name': 'test1',
            'access_token': '2'
        })

        self.assertEqual(response.status_code, 200)
        
        account = Account.objects.get(pk=self.aid)
        self.assertEqual(account.name, 'test1')
        self.assertEqual(account.access_token, '2')

    def test_empty_token(self):
        """ Токен не должен изменяться, если передано пустое значение """

        response = self.client.post(reverse('manager_account_update'), {
            'account_id': self.aid,
            'name': 'test2',
            'access_token': ''
        })

        self.assertEqual(response.status_code, 200)
        
        account = Account.objects.get(pk=self.aid)
        self.assertEqual(account.name, 'test2')
        self.assertEqual(account.access_token, '1')

class AddCampaignTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')

    def test_add(self):
        """ Обычный сценарий добавления """

        response = self.client.post(reverse('manager_campaign_add'), { 'name': 'test1' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Campaign.objects.filter(manager=self.manager, name='test1')), 1)
        self.assertEqual(json.loads(response.content)['error'], False)

        response = self.client.post(reverse('manager_campaign_add'), { 'name': u'ЮНИКОДА' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Campaign.objects.filter(manager=self.manager, name=u'ЮНИКОДА')), 1)
        self.assertEqual(json.loads(response.content)['error'], False)

    def test_same_name(self):
        """ Попытка добавить кампанию с таким же названием """

        response = self.client.post(reverse('manager_campaign_add'), { 'name': 'test1' })
        response = self.client.post(reverse('manager_campaign_add'), { 'name': 'test1' })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Campaign.objects.all()), 1)
        self.assertEqual(json.loads(response.content)['error'], True)


class UpdateCampaignTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')
        self.campaign1_id = Campaign.objects.create(manager=self.manager, name='test').pk

    def test_basic(self):
        """ Обычный сценарий изменения кампании """
        response = self.client.post(reverse('manager_campaign_update'), {
            'campaign_id': self.campaign1_id,
            'name': 'test2'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Campaign.objects.get(pk=self.campaign1_id).name, 'test2')
        self.assertEqual(len(Campaign.objects.all()), 1)
        self.assertEqual(json.loads(response.content)['error'], False)

    def test_same_name(self):
        """ Повторное имя """
        self.campaign2_id = Campaign.objects.create(manager=self.manager, name='test2').pk

        response = self.client.post(reverse('manager_campaign_update'), {
            'campaign_id': self.campaign2_id,
            'new_name': 'test'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Campaign.objects.get(pk=self.campaign1_id).name, 'test')
        self.assertEqual(Campaign.objects.get(pk=self.campaign2_id).name, 'test2')
        self.assertEqual(json.loads(response.content)['error'], True)

class DeleteCampaignTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.campaign1 = Campaign.objects.create(manager=self.manager, name='test1')
        self.campaign2 = Campaign.objects.create(manager=self.manager, name='test2')
        self.campaign3 = Campaign.objects.create(manager=self.manager, name='test3')

        self.post = VkPost.objects.create(
            campaign = self.campaign1,
            access_token='test',
            when_to_post=datetime.now() + timedelta(seconds=60),
            when_to_delete=datetime.now() + timedelta(seconds=240), 
            owner_ids='-1',
            text='Hello, world!',
            from_group=True,
            attachments=''
        )
        VkPostEvent.objects.create(post=self.post, event_id=1)
        VkPostEvent.objects.create(post=self.post, event_id=2)

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.mox = mox.Mox()
        self.mox.StubOutWithMock(helpers, 'send_to_scheduler')

        helpers.send_to_scheduler(mox.IgnoreArg())

        self.mox.ReplayAll()


    def test_basic(self):

        response = self.client.post(reverse('manager_campaign_delete'), {
            'ids[]': [self.campaign1.pk, self.campaign3.pk]
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], False)
        self.assertEqual(len(Campaign.objects.all()), 1)
        self.assertEqual(Campaign.objects.get(name='test2').pk, self.campaign2.pk)
        self.assertEqual(VkPost.objects.all().count(), 0)
        self.mox.VerifyAll()

    def tearDown(self):
        self.mox.UnsetStubs()

class AddPostTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')

    def test_not_own_campany(self):
        """ Проверить недоступность страницы добавления поста в не свою кампанию """

        response = self.client.get(reverse('manager_post_add', args=(0,)))
        self.assertEqual(response.status_code, 404)

class SubmitPostTest(TestCase):
    
    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')
        self.account = Account.objects.create(manager=self.manager, name='account', access_token='token')
        self.campaign = Campaign.objects.create(manager=self.manager, name='Test')

        self.mox = mox.Mox()
        self.mox.StubOutWithMock(helpers, 'send_to_scheduler')
        helpers.send_to_scheduler(mox.IgnoreArg())
        helpers.send_to_scheduler(mox.IgnoreArg())
        self.mox.ReplayAll()


    def test_add_basic(self):
        """ Базовый сценарий добавления """

        posting_time = datetime.utcnow() + timedelta(seconds=120)
        delete_time = datetime.utcnow() + timedelta(seconds=240)

        response = self.client.post(reverse('set_timezone'), {
            'timezone': 'Europe/London'
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': posting_time.strftime('%d.%m.%Y %H:%M'),

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': delete_time.strftime('%d.%m.%Y %H:%M'),

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'chain',

           'editor_data': '{"groups": [{"gid": "1"}, {"gid": "2"}, {"gid": "3"}]}'
        })

        self.assertEqual(json.loads(response.content)['error'], False)
        self.assertEqual(response.status_code, 200)
        self.mox.VerifyAll()

        post = VkPost.objects.filter(campaign=self.campaign)[0]
        self.assertEqual(post.access_token, 'token')
        self.assertEqual(post.text, 'Hello, world!')
        self.assertLess(
            abs((post.when_to_post - posting_time.replace(tzinfo=pytz.utc)).total_seconds()),
            60
        )
        self.assertLess(
            abs((post.when_to_delete - delete_time.replace(tzinfo=pytz.utc)).total_seconds()),
            60
        )
        self.assertEqual(post.attachments, 'photo1_1,video1_1,audio1_1')

    def test_empty_message_attachments(self):
        """ Когда не указано сообщение или не прикреплен ни один ресурс """

        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': '01.01.1970 01:01',

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': '01.01.1970 01:05',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'chain'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)


    def test_post_schedule(self):
        """ 
        Тестирование размещение по расписанию
            -- выбран режим, не указанов время
            -- время находится в прошлом
        """
        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': '',

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': '01.01.1970 01:05',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'chain'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)

        response = self.client.post(reverse('manager_post_submit'), {
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': (datetime.utcnow() + timedelta(seconds=5*3600)).strftime('%Y.%h.%m %H:%i'),

           'when_to_delete_mode': 'schedule',
           'when_to_delete_timestamp': '01.01.1970 01:05',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'chain'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)


    def test_delete_schedule(self):
        """
        Тестирование времени удаления по расписанию
            -- выбран режим, но не указано время
            -- время находится в прошлом или меньше времени размещения
        """
        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': '01.01.1970 01:01',

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': '',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'chain'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)

        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': '01.01.1970 01:01',

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': '01.01.1969 01:01',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'chain'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)


    def test_account_empty(self):
        """ Если не выбран аккаунт """

        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': -1,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': '01.01.1970 01:01',

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': '01.01.1970 01:05',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'chain'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)

    def test_empty_groups(self):
        """ Выбрана ни одна группа """
        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': '01.01.1970 01:01',
           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': '01.01.1970 01:05',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': None,
           'posting_mode': 'chain'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)

    def test_no_posting_mode(self):
        """ Не выбран режим постинга """

        response = self.client.post(reverse('manager_post_submit'), {
           'campaign': self.campaign.pk,
           'posting_account': self.account.pk,
           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': '01.01.1970 01:01',
           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': '01.01.1970 01:05',

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], True)


    def tearDown(self):
        self.mox.UnsetStubs()

class UpdatePostTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')
        self.account = Account.objects.create(manager=self.manager, name='account', access_token='token')
        self.campaign = Campaign.objects.create(manager=self.manager, name='Test')
        self.post = VkPost.objects.create(
            campaign = self.campaign,
            access_token='test',
            when_to_post=datetime.now() + timedelta(seconds=60),
            when_to_delete=datetime.now() + timedelta(seconds=240), 
            owner_ids='-1',
            text='Hello, world!',
            from_group=True,
            attachments=''
        )

        VkPostEvent.objects.create(post=self.post, event_id=1, event_type='add')
        VkPostEvent.objects.create(post=self.post, event_id=2, event_type='delete')

        self.mox = mox.Mox()
        self.mox.StubOutWithMock(helpers, 'send_to_scheduler')
        helpers.send_to_scheduler(mox.IgnoreArg())
        self.mox.ReplayAll()


    def test_update_basic(self):
        """ Базовый сценарий обновления """

        posting_time = datetime.utcnow() + timedelta(seconds=120)
        delete_time = datetime.utcnow() + timedelta(seconds=240)

        response = self.client.post(reverse('set_timezone'), {
            'timezone': 'Europe/London'
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('manager_post_update', args=(self.post.pk,)), {
           'campaign': self.campaign.pk,
           'post': self.post.pk,
           'posting_account': self.account.pk,

           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': posting_time.strftime('%d.%m.%Y %H:%M'),

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': delete_time.strftime('%d.%m.%Y %H:%M'),

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3',
           'posting_mode': 'one_at_a_time',
           'editor_data': '{"groups": [{"gid": "1"}, {"gid": "2"}, {"gid": "3"}]}'
        })

        self.assertEqual(json.loads(response.content)['error'], False)
        self.assertEqual(response.status_code, 200)
        self.mox.VerifyAll()

        post = VkPost.objects.get(pk=self.post.pk)
        self.assertEqual(post.access_token, 'token')
        self.assertEqual(post.text, 'Hello, world!')
        self.assertLess(
            abs((post.when_to_post - posting_time.replace(tzinfo=pytz.utc)).total_seconds()),
            60
        )
        self.assertLess(
            abs((post.when_to_delete - delete_time.replace(tzinfo=pytz.utc)).total_seconds()),
            60
        )
        self.assertEqual(post.attachments, 'photo1_1,video1_1,audio1_1')

    def test_posted(self):
        """ Проверка попытки изменения уже размещенного поста """
        self.post.status = 'posted'
        self.post.save()

        posting_time = datetime.utcnow() + timedelta(seconds=120)
        delete_time = datetime.utcnow() + timedelta(seconds=240)

        response = self.client.post(reverse('manager_post_update', args=(self.post.pk,)), {
           'post': self.post.pk,
           'posting_account': self.account.pk,

           'when_to_post_mode': 'schedule',
           'post_schedule_timestamp': posting_time.strftime('%d.%m.%Y %H:%M'),

           'when_to_delete_mode': 'schedule',
           'delete_schedule_timestamp': delete_time.strftime('%d.%m.%Y %H:%M'),

           'from_group': True,

           'text': 'Hello, world!',
           'attachments': 'photo1_1,video1_1,audio1_1',
           'groups': '1,2,3'
        })

        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.mox.UnsetStubs()

class DeletePostTest(TestCase):

    def setUp(self):
        self.manager = Manager.objects.create_user(uid=1, network='vk')

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.account = Account.objects.create(manager=self.manager, name='account', access_token='token')
        self.campaign = Campaign.objects.create(manager=self.manager, name='Test')

        self.post = VkPost.objects.create(
            campaign = self.campaign,
            access_token='test',
            when_to_post=datetime.now() + timedelta(seconds=60),
            when_to_delete=datetime.now() + timedelta(seconds=240), 
            owner_ids='-1',
            text='Hello, world!',
            from_group=True,
            attachments=''
        )
        VkPostEvent.objects.create(post=self.post, event_id=1)
        VkPostEvent.objects.create(post=self.post, event_id=2)

        self.client = Client()
        self.client.login(uid=1, network='vk')

        self.mox = mox.Mox()
        self.mox.StubOutWithMock(helpers, 'send_to_scheduler')

        helpers.send_to_scheduler(mox.IgnoreArg())

        self.mox.ReplayAll()

    def test_basic(self):
        """ Тестирование удаления """

        response = self.client.post(reverse('manager_post_delete'), {
            'posts[]': [self.post.pk]
        })

        self.mox.VerifyAll()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['error'], False)
        self.assertEqual(len(VkPost.objects.filter(pk=self.post.pk)), 0)

    def tearDown(self):
        self.mox.UnsetStubs()


class GetAccessTokenCase(TestCase):

    url = 'https://oauth.vk.com/blank.html#access_token=b2be2f209833db91f55474716fe7a277f0755f908b90e59a5a0037ad60ab1a107bf7ede92e731d4906220&expires_in=0&user_id=156261930'

    token = 'b2be2f209833db91f55474716fe7a277f0755f908b90e59a5a0037ad60ab1a107bf7ede92e731d4906220'

    def test_simple(self):

        self.assertEqual(get_access_token(self.token), self.token)

    def test_extract(self):

        self.assertEqual(get_access_token(self.url), self.token)

