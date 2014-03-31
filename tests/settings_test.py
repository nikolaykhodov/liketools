# -*- coding: utf-8 -*-

'''
Юнит-тесты для проверки правильности настроек
'''

import unittest
import settings as set1
import web.settings as set2

class SettingsCase(unittest.TestCase):
    '''
    Проверка одинаковости глобальных настроек
    '''

    def test_1(self):
        self.assertEqual(set1.RABBITMQ_HOST, set2.RABBITMQ_HOST)
        self.assertEqual(set1.POSTING_QUEUE, set2.POSTING_QUEUE)
        self.assertEqual(set1.SCHEDULER_QUEUE, set2.SCHEDULER_QUEUE)
