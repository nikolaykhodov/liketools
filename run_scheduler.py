# -*- coding: utf8 -*-

""" Демон планировщика """

from scheduler.core import Scheduler
from scheduler.helpers import add_event_id

from multiprocessing import Process, Queue
from utils import setup_logging, import_class, send_to_queue
from datetime import datetime
from threading import Thread

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import time
import settings
import logging
import pika
import json
import sys, os

class SchedulerMessageHandler(object):
    """
    Обработчик входящих сообщений
    """
    
    def __init__(self, scheduler):
        """ Конструктор """
        self.scheduler = scheduler
        engine = create_engine(settings.SCHEDULER_DB_PERSISTENT_STORAGE, pool_recycle=3600)
        self.session_maker = sessionmaker(bind=engine, autocommit=True)
        
    def add(self, message):
        """ Добавить пост в расписание """


        data = message.get('data', {})
        
        # Добавить событие
        event_id = self.scheduler.add(
                      trigger_time=message.get('trigger_time'),
                      **data)


        # Прописать значение event_id
        lt_post_id = data.get('lt_post_id')
        if lt_post_id:
            add_event_id(self.session_maker(), lt_post_id, event_id, data.get('action', ''))

        # Записать в лог
        logging.debug("Added action with id=%s (trigger|delay_time=%s) with data=%s", 
                      event_id, 
                      message.get('delay_time') or datetime.fromtimestamp(int(message['trigger_time'])).strftime('%Y-%m-%d %H:%M:%S'), 
                      data)
        
    def delete(self, messages):
        """ Удалить пост из очереди """

        if not isinstance(messages, list):
            messages = [messages]

        for message in messages:
            self.scheduler.delete(event_id=message.get('event_id'))
            logging.debug("Deleted event with id=%s", message.get('event_id'))

    def update(self, message):
        """ Обновить информацию о посте """

        self.scheduler.update(event_id=message.get('event_id'),
                         new_trigger_time=message.get('new_trigger_time'),
                         **message.get('new_data'))

        logging.debug("Updated event with id=%s: new_trigger_time=%s, new_data=%s", message.get('event_id'), message.get('new_trigger_time'), message.get('new_data'))

    def mark_as_processed(self, message):
        """ Пометить событие как обработанное """

        self.scheduler.mark_as_processed(event_id=message.get('event_id'))

        logging.debug('Marked event (id=%s) as processed', message.get('event_id'))



    def dispatch(self, message):
        """ Выбрать правильный метод для обработки сообщений """

        try:
            getattr(self, message.get('action'))
        except (AttributeError, TypeError):
            return

        self.__getattribute__(message.get('action'))(message)

def inc_message_thread(queue, scheduler):
    """ Поток внутри процесса планировщика для обработки сообщений из очереди """

    handler = SchedulerMessageHandler(scheduler)
    while 1:
        time.sleep(1.0)

        # Read new commands
        message = {}
        while message is not None:
            # Read new message from queue
            try:
                message = queue.get_nowait()
            except:
                message = None
                continue

            try:
                handler.dispatch(message) 
            except Exception, exc:
                logging.exception(exc)

def scheduler_process(queue, ppid):
    """ Процесс для работы планировщика """

    ram_class = import_class(settings.SCHEDULER_RAM_STORAGE)
    persist_class = import_class(settings.SCHEDULER_PERSISTENT_STORAGE)
    scheduler = Scheduler(
        ram_storage=ram_class(), 
        persist_storage=persist_class(
            settings.SCHEDULER_DB_PERSISTENT_STORAGE,
            pool_recycle=settings.POOL_RECYCLE,
            pool_size=settings.POOL_SIZE
        )
    )

    # Thread for immediate running of incoming commands
    Thread(target=inc_message_thread, args=(queue, scheduler, )).start()
    
    logging.info("Restoring previous events...")
    scheduler.restore()
    logging.info("Restoring completed.")

    period = 15 if settings.DEBUG is False else 5
    start_time = time.time()
    counter = 0

    while 1:
        # Kill himself if parent is killed
        if os.getppid() != ppid:
            sys.exit()

        #do something
        events = scheduler.get_events()

        for event in events:
            scheduler.mark_as_processing(event.event_id)

            logging.debug("Event (id=%s) marked as processing", event.event_id)
            logging.debug("Sending event (id=%s) to posting queue...", event.event_id)

            message = dict(event_id=event.event_id)
            message.update(event.data)
            send_to_queue(settings.RABBITMQ_HOST, settings.POSTING_QUEUE, message)

        allowance = time.time() - counter*period - start_time
        logging.debug(" [x] allowance = %s, counter = %s, per cent of period = %s", allowance, counter, int(allowance/period * 100))

        if allowance > period/3.0:
            if period - allowance >= 0.0:
                time.sleep(period - allowance)
            else:
                time.sleep(0.1)

            counter = -1
            start_time = time.time()
        else:
            time.sleep(period)

        counter += 1


def amqp_thread(queue):
    """ Процесс приема сообщений из очереди posting_queue и отправки во внутреннюю очередь """

    def process_message(channel, method, properties, body):
        try:
            message = json.loads(body)
            queue.put(message)
        except (TypeError, ValueError):
            logging.error("Not JSON-encoded message received: %s", body)
        finally:
            channel.basic_ack(delivery_tag = method.delivery_tag)
        
    connection = pika.BlockingConnection(pika.ConnectionParameters( host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.SCHEDULER_QUEUE, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(process_message, queue=settings.SCHEDULER_QUEUE)
    channel.start_consuming()

def start():
    """ Запуск планировщика """
    setup_logging(logging.DEBUG if settings.DEBUG is True else logging.INFO)
    queue = Queue()

    # Start scheduler subprocess
    Process(target=scheduler_process, args=(queue, os.getpid())).start()

    
    # To support Ctrl+C in debug mode
    if not settings.DEBUG:
        Thread(target=amqp_thread, args=(queue, )).start()
    else:
        Process(target=amqp_thread, args=(queue, )).start()

if __name__ == '__main__':
    start()

