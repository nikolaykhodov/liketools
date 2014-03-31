# -*- encoding: utf-8 -*-
'''
Модуль для доступа к API ВКонтакте
'''

from urllib import urlencode
from urllib2 import HTTPError

import re
import urllib2
import json
import logging

class APIError(Exception):
    '''
    Исключение при работе c API
    '''
    
class CaptchaNeeded(Exception):
    """
    Требуется капча для продолжения
    
    Параметры:
        -- sid - номер сессии для капчи
        -- img - ссылка на изображение капчи
    """
    def __init__(self, sid, img):
        self.sid = sid
        self.img = img

class APIProxy(object):
    '''
    Класс-посредник, позволяющий вызывать методы API ВКонтакте, не описывая их 
    в коде
    '''
    def __init__(self, api, prefix=''):
        '''
        api    -- объект класса API
        prefix -- префикс перед названиями методов. Если не пустая строка, то 
                  имя метода формируется как <prefix>.<method>, иначе <method>.
        '''
        self.api = api
        self.prefix = prefix
        self.methods = {}
        
    def get_method_name(self, name):
        '''
        Возвращает имя непосредственное имя метода для запроса к API ВКонтакте
        '''
        return ('' if self.prefix == '' else self.prefix + '.') + name
    
    def __getattr__(self, name):
        '''
        Метод-заглушка для формирования запросов к API с динамическими 
        названиями методов
        '''
        def method(*args, **kwargs):
            '''
            Метод, непосредственно выполняющий запрос
            '''
            args = kwargs
            args['access_token'] = self.api.access_token
            url = 'https://api.vk.com/method/' + self.get_method_name(name) + '?' 
            
            logging.info('https://api.vk.com/method/' + self.get_method_name(name) + '?' + urlencode(dict(args)))
            
            response = urllib2.urlopen(url, urlencode(dict(args)), 5).read()

            answer = json.loads(response)
            try:
                return answer['response']
            except (KeyError):
                if answer['error']['error_code'] == 14:
                    raise CaptchaNeeded(answer['error']['captcha_sid'], answer['error']['captcha_img'])
                else:
                    raise APIError, "%s (code %s)" % (answer['error']['error_msg'], answer['error']['error_code'])
            except (HTTPError):
                raise APIError, "API is down"
        
        if name not in self.methods:
            self.methods[name] = method

        return self.methods[name]

class API(object):
    '''
    Класс для запросов к API ВКонтакте
    '''
    def __init__(self, access_token):
        '''
        access_token -- токен
        '''
        self.access_token = access_token

        # обертка для простых методов        
        self.methods = APIProxy(self)
        prefixes = ['likes', 'friends', 'groups', 'photos', 'wall', 'newsfeed', 
                    'audio', 'video', 'docs', 'places', 'secure', 'storage', 
                    'notes', 'pages', 'offers', 'questions', 
                    'subscriptions', 'messages']
        # обертка для вложенные методов
        for prefix in prefixes:
            setattr(self, prefix, APIProxy(self, prefix))
            
        self.cached_names = {}
            
    def __getattr__(self, name):
        '''
        Позволяет обращаться к методам без префикса
        '''
        return self.methods.__getattr__(name)          
        
    @staticmethod
    def create_requests_sequence(start, end, count):
        '''
        Возвращает последовательность пар (смещение, кол-во запрашиваемых
        элементов) для получения элементов со start по end
        
        count -- разме выборки
        '''
        if start > end: 
            raise Exception, "start must be greater than end"
        if end - start  <= count:
            return [(start-1, end - start + 1)]    
            
        sequence = [(i*count+start-1, count) for i in xrange(0, (end-start)/count)]
        if end % count > 0:
            sequence.append(((end-start)/count * count, end % count))
        else:
            sequence.append(((end-start)/count * count, count))
            
        return sequence

    def resolve_names(self, ids):
        '''
        Выполняет резолвинг имен, которые не в формате 
        id<номер пользователя ВКонтакте>
        
        ids -- список идентификаторов пользователей
        '''
        ids_map = dict([[mid, mid] for mid in ids])
        
        to_resolve = []
        for mid in ids:
            if mid in self.cached_names:
                ids_map[mid] = self.cached_names[mid]
            elif len(re.findall(r'^id\d+$', mid)) > 0:
                ids_map[mid] = int(mid.replace('id', ''))
                self.cached_names[mid] = ids_map[mid]
            else:
                to_resolve.append(mid)
                
        if len(to_resolve) > 0:
            sequence = self.create_requests_sequence(1, len(to_resolve), 1000)
            for start, count in sequence:
                part = to_resolve[start:start+count]
                
                answer = self.getProfiles(
                    uids=",".join(part),
                    fields='uid'
                )
                for i in xrange(len(part)):
                    ids_map[part[i]] = answer[i]['uid']
                    self.cached_names[part[i]] = answer[i]['uid']
                
        return ids_map          
