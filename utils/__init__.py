# -*- coding: utf8 -*-

import multiprocessing
import logging
import StringIO
import threading
import time
import Queue
import pika
import json

class MultiProcessingLogHandler(logging.Handler):
    def __init__(self, handler, queue, child=False):
        logging.Handler.__init__(self)

        self._handler = handler
        self.queue = queue

        # we only want one of the loggers to be pulling from the queue.
        # If there is a way to do this without needing to be passed this
        # information, that would be great!
        if child == False:
            self.shutdown = False
            self.polltime = 1
            t = threading.Thread(target=self.receive)
            t.daemon = True
            t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        #print "receive on"
        while (self.shutdown == False) or (self.queue.empty() == False):
            # so we block for a short period of time so that we can
            # check for the shutdown cases.
            try:
                record = self.queue.get(True, self.polltime)
                self._handler.emit(record)
            except Queue.Empty, e:
                pass

    def send(self, s):
        # send just puts it in the queue for the server to retrieve
        self.queue.put(s)

    def _format_record(self, record):
        ei = record.exc_info
        if ei:
            dummy = self.format(record) # just to get traceback text into record.exc_text
            record.exc_info = None  # to avoid Unpickleable error

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        time.sleep(self.polltime+1) # give some time for messages to enter the queue.
        self.shutdown = True
        time.sleep(self.polltime+1) # give some time for the server to time out and see the shutdown

    def __del__(self):
        self.close() # hopefully this aids in orderly shutdown when things are going poorly.

def setup_logging(level=logging.INFO):
    stream = StringIO.StringIO()
    logQueue = multiprocessing.Queue(100)
    handler = MultiProcessingLogHandler(logging.StreamHandler(stream), logQueue)

    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(level)

def import_class(kls):
    """
    Import class by string name
    """

    path = kls.split('.')
    module = ".".join(path[:-1])
    cls = path[-1]
    

    mod = __import__(module, fromlist=['a'])
    return getattr(mod, cls)

def send_to_queue(host, queue, message):
    """
    Send message about posting 
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters( host=host ))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(exchange='', 
                            routing_key=queue, 
                            body=json.dumps(message),  
                            properties=pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                           ))
    connection.close()


