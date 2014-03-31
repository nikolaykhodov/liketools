# -*- coding: utf8 -*-
""" Poster """

import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

from gevent import Greenlet, sleep

from utils import setup_logging, send_to_queue
from api.vk import API, APIError, CaptchaNeeded 
from api.captcha import CaptchaRecognizer
from api.captcha import NoSlotsError, InvalidFileError, InvalidCaptchaIDError, UnknownError, TimeoutAntigateError

from scheduler.models import VkPost
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

import settings
import logging
import pika
import json
import time

class PosterMessageHandler(object):
    """
    Обработчик входящих сообщений
    """

    def __init__(self):
        """ Конструктор """
        engine = create_engine(
                settings.SCHEDULER_DB_PERSISTENT_STORAGE, 
                pool_recycle=settings.POOL_RECYCLE, 
                pool_size=settings.POOL_SIZE
        )
        self.session_maker = sessionmaker(bind=engine, autocommit=True)

    def _post(self, message, captcha_sid='', captcha_key='', owner_id=''):
        api = API(message.get('access_token'))

        message_text = message.get('text').encode('utf-8') or ""
        from_group = message.get('from_group') or 0
        attachments = message.get('attachments') or ""

        return api.wall.post(
            message = message_text,
            owner_id = owner_id,
            from_group = from_group,
            attachments = attachments,
            captcha_sid=captcha_sid,
            captcha_key=captcha_key
        )['post_id']

    def add(self, message):
        """ Добавить пост на стену """

        # Задержка между двумя постами
        try:
            posting_delay = float(message.get('posting_delay', settings.POSTING_DELAY))
            if posting_delay < 0:
                posting_delay = 0.1
        except ValueError:
            posting_delay = settings.POSTING_DELAY


        owner_ids = message.get('owner_ids', [])
        if not isinstance(owner_ids, list):
            owner_ids = [owner_ids]

        # Ссылки на посты
        links = {}
        errors = False
        # Разместить посты
        for owner_id in owner_ids:
            post_id = None

            log_message = u''
            try:
                post_id = self._post(message, owner_id=owner_id)
                log_message = log_message + u'Successfully posted'

                logging.debug("Posted with id=%s%s", 
                              "https://vk.com/wall%s_" % owner_id, 
                              post_id
                )

            except APIError, exc:
                # Ошибки при размещении постов
                errors = True

                # Отобразить в логе
                logging.exception("APIError:\nMessage = %s\n", message)
                log_message = u'Error occured:\n' + unicode(exc)
            except CaptchaNeeded, exc:
                # Ошибки при размещении постов
                errors = True

                # Отобразить в логе
                logging.debug("VK.COM requires captcha")

                # Получить параметры для распознавания капчи
                antigate_key = message.get('antigate_key', '')
                
                # Количество попыток
                try:
                    attempts = int(message.get('captcha_attempts', settings.CAPTCHA_ATTEMPTS))
                    if attempts < 0:
                        attempts = 0
                except ValueError:
                    attempts = settings.CAPTCHA_ATTEMPTS


                # Время ожидания
                try:
                    wait_time = float(message.get('captcha_attempts_delay', settings.CAPTCHA_ATTEMPTS_DELAY))
                    if wait_time < 0:
                        wait_time = 0.1
                except ValueError:
                    wait_time = settings.CAPTCHA_ATTEMPTS_DELAY
                    
                # Старт распознавания
                recognizer = CaptchaRecognizer(
                    antigate_key, 
                    sleep_func=sleep,
                    attempts=attempts,
                    wait_time=wait_time
                )
                try:
                    value = recognizer.recognize(exc.img)
                    logging.debug("Value of %s is %s", exc.img, value)

                    post_id = self._post(message, captcha_sid=exc.sid, captcha_key=value, owner_id=owner_id)

                    log_message = u'Successfully posted after captcha recognition'
                except NoSlotsError:
                    log_message = u'No slots available'
                except InvalidFileError:
                    log_message = u'File of %s is invalid' % exc.img
                except InvalidCaptchaIDError:
                    log_message = u'Somehow Liketools is passed invalid captcha ID'
                except UnknownError, exc:
                    log_message = u'Unknown Antigate Error: ' + unicode(exc)
                except TimeoutAntigateError:
                    log_message = u'Timeout on waiting of recognition'
                except APIError, exc:
                    logging.exception("APIError:\nMessage = %s\n", message)
                    log_message = u'Error occured:\n' + unicode(exc)
                except CaptchaNeeded, exc:
                    log_message = u'VK.COM requires one more time'

                logging.debug(log_message)

            # Добавить лог и ссылку в массив перед сохранением в базу данных
            links[owner_id] = {
                'log': log_message,
                'timestamp': int(time.mktime(datetime.utcnow().timetuple()))
            }
            
            if post_id:
                links[owner_id].update({ 'post_id': post_id })

            gevent.sleep(posting_delay)

        links.update(dict(
            errors=errors,
            deleted=None,
            posted=int(time.mktime(datetime.utcnow().timetuple()))
        ))
        # Записать лог и ссылки на пост 
        session = self.session_maker()
        session.begin()
        try:
            post = session.query(VkPost).filter(VkPost.id == message.get('lt_post_id')).first()
            post.links = links
            post.status = 'posted' if not errors else 'with_errors'
            session.commit()
        except Exception:
            logging.exception("Can't write to DB\nMessage = %s\n", message)
            session.rollback()
        finally:
            session.close()


    def delete(self, message):
        """ Удалить пост со стены """

        posts = []
        
        # Сформировать список ссылок для удаления по посту из базы данных
        lt_post_id = message.get('lt_post_id', None)
        if lt_post_id is not None:
            
            # Пост
            session = self.session_maker()
            try:
                vk_post = session.query(VkPost).filter(VkPost.id == lt_post_id).first()
            except Exception:
                logging.exception("Message = %s\nException:\n", message)
            finally:
                session.close()

            # Список размещенных постов
            for owner_id in vk_post.links:
                # Пропускать служебные свойства
                if not isinstance(vk_post.links[owner_id], dict):
                    continue

                post_id = vk_post.links[owner_id].get('post_id', '')

                if post_id != '':
                    posts.append((owner_id, post_id))

        else:
            owner_id = message.get('owner_id') or ""
            post_id = message.get('post_id') or ""

            posts.append((owner_id, post_id))

        api = API(message.get('access_token'))

        for owner_id, post_id in posts:
            try:
                api.wall.delete(
                    owner_id=owner_id,
                    post_id=post_id
                )

                logging.debug("Deleted post: http://vk.com/wall%s_%s", owner_id, post_id)
            except APIError:
                logging.exception("Message = %s\nException:\n", message)

        # Записать информацию об удалении 
        if lt_post_id is not None:
            session = self.session_maker()
            session.begin()
            try:
                post = session.query(VkPost).filter(VkPost.id == lt_post_id).first()

                # Т.к. словарь - это объект, то надо завести новый, чтобы SQLAlchemy определил изменение
                new_links = {}
                new_links.update(post.links)
                new_links['deleted'] = int(time.mktime(datetime.utcnow().timetuple()))

                # Записать в базу
                post.links = new_links
                session.commit()
            except Exception:
                logging.exception("Can't write to DB\nMessage = %s\n", message)
                session.rollback()
            finally:
                session.close()

    def dispatch(self, message):
        """ Выбирает метод для обработки сообщения """

        try:
            getattr(self, message.get('action'))
        except AttributeError:
            return

        self.__getattribute__(message.get('action'))(message)

        # Подтвердить успешное выполнение
        event_id = message.get('event_id')
        if event_id and message.get('action') != 'set_event_id':
            send_to_queue(settings.RABBITMQ_HOST, settings.SCHEDULER_QUEUE, dict(
                action="mark_as_processed",
                event_id=event_id
            ))


def amqp_thread(handler):
    """ Поток для получения входящих сообщений и отправку их в очередь на исполнение """

    def process_message(channel, method, properties, body):
        logging.debug("Received message: %s", body)
        try:
            message = json.loads(body)
        except (TypeError, ValueError):
            logging.error("Not JSON-encoded message received: %s", body)

        try:
            Greenlet.spawn(handler.dispatch, message)
        except Exception:
            logging.exception("Unhandled exception: \n Message = %s\n\n", body)

        channel.basic_ack(delivery_tag = method.delivery_tag)
        
    connection = pika.BlockingConnection(pika.ConnectionParameters( host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.POSTING_QUEUE, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(process_message, queue=settings.POSTING_QUEUE)
    channel.start_consuming()

def start():
    """ Подготовка """
    setup_logging(logging.DEBUG)
    handler = PosterMessageHandler()
    amqp_thread(handler)

if __name__ == '__main__':
    start()
