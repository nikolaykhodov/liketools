# -*- coding: utf-8 -*-

'''
Юнит-тесты для прототипа TopFuns
'''

REFRESH_TOKEN_URL = 'https://oauth.vk.com/authorize?client_id=2688740&scope=friends,wall,offline,photo,audio,video,groups&redirect_uri=http://oauth.vk.com/blank.html&display=page&response_type=token'
TOKEN = 'c8318736c161d91cc161d91c01c148dff8cc170c164f9069119df7b1f55d82954726ab9'

import unittest
from api.vk import API, APIError
from urllib2 import URLError
import logging

class APITest(unittest.TestCase):
    '''
    Тестирование работоспособности класса для работы с API
    '''

    def __init__(self, *args, **kwargs):
        super(APITest, self).__init__(*args, **kwargs)

        api = API(TOKEN)
        try:
            api.friends.get()
        except APIError:
            print "Token is invalid or expires. Try to refresh token by using this url " + REFRESH_TOKEN_URL
        except URLError:
            print "No connection"
    
    def setUp(self):
        self.api = API(TOKEN)
        logging.basicConfig(level=logging.DEBUG)

    def test_basic(self):
        answer = self.api.getProfiles(uids='durov,andrew')

        self.assertEqual(answer[0]['uid'], 1)
        self.assertEqual(answer[1]['uid'], 6492)      
        self.assertEqual(self.api.isAppUser(), "1")  

    def test_wall(self):

        # Add post
        post = self.api.wall.post(message='You are welcome!')
        post_id = post['post_id']

        # Get my ID
        wall = self.api.wall.get()
        mid = wall[1]['to_id']
        post_id = str(mid) + '_' + str(post_id)
        print post_id

        # Get post
        self.assertEqual(self.api.wall.getById(posts=post_id)[0]['id'], post['post_id'])

        # Remove post
        self.api.wall.delete(post_id=post['post_id'])


