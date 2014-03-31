# -*- coding: utf8 -*-

"""

A Scheduler class

"""
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from threading import RLock
import time
import settings
from datetime import datetime

class SchedulerError(Exception):
    pass

class Scheduler(object):

    def __init__(self, ram_storage, persist_storage):
        """ Constructor

        Arguments:
            ram_storage -- storage for in-memory processing events
            persist_storage -- storage for saving events
        """
        
        self.ram = ram_storage
        self.persist = persist_storage

        self.engine = create_engine(settings.SCHEDULER_DB_PERSISTENT_STORAGE)
        self.Session = sessionmaker(bind=self.engine, autocommit=True)

        inspector = Inspector.from_engine(self.engine)
        if not "main_vkpost" in inspector.get_table_names():
            raise SchedulerError, "There is not 'main_vkpost' table"

        self.lock = RLock()

    def dt2timestamp(self, dt):
        """ Convert datetime object to UNIX timestamp """

        return int(time.mktime(dt.timetuple()))

    def timestamp2dt(self, timestamp):
        """ Convert UNIX timestamp to datetime object """

        return datetime.fromtimestamp(timestamp)

    def add(self, trigger_time=None, delay_time=None, **kwargs):
        """ 
        Add event to queue. You should pass only one of two arguments (trigger_time or delay_time).

        Arguments:
            trigger_time -- time since epoch in seconds in UTC+0
            delay_time   -- trigger_time = time() + delay_time
        """

        if (trigger_time is None and delay_time is None) or (trigger_time is not None and delay_time is not None):
            raise SchedulerError, "Only one time parameter should be passed"

        if trigger_time is not None:
            event_time = int(trigger_time)

        if delay_time is not None:
            event_time = self.dt2timestamp(datetime.utcnow()) + delay_time 

        self.lock.acquire()
        try:
            event_id = self.persist.add(event_time=event_time, **kwargs)
            self.ram.add(event_id=event_id, event_time=event_time / 60, **kwargs)
        finally:
            self.lock.release()

        return event_id
            
    def delete(self, event_id):
        """
        Delete event from queue.

        Arguments:
            event_id -- id of event to be deleted.
        """

        self.lock.acquire()
        try:
            self.ram.delete(event_id=event_id)
            self.persist.delete(event_id=event_id)
        finally:
            self.lock.release()

    def get_events(self, needle_time=None):
        """
        Return list of events which will be fired in minute specified by needle_time.

        Arguments:
            needle_time -- time in seconds since epoch
        """

        if needle_time is None:
            needle_time = int(self.dt2timestamp(datetime.utcnow()) / 60)
        else:
            needle_time = int(needle_time / 60)

        self.lock.acquire()
        try:
            return self.ram.get_events(from_event_time=needle_time, to_event_time=needle_time)
        finally:
            self.lock.release()

    def restore(self):
        """ Load all events from persistent storage """
        self.lock.acquire()
        try:
            current_time = self.dt2timestamp(datetime.utcnow())
            for event in self.persist.all(from_time=current_time):
                self.ram.add(event_id=event.id, event_time=event.event_time / 60, **event.data)
        finally:
            self.lock.release()

    def update(self, event_id, new_trigger_time, **new_data):
        """
        Update event

        Arguments:
            -- new_trigger_time - 
            -- new_data - 
        """

        event_time = int(new_trigger_time)
        self.lock.acquire()
        try:
            self.ram.update(event_id, event_time / 60, **new_data)
            self.persist.update(event_id, event_time, **new_data)
        finally:
            self.lock.release()

    def mark_as_processing(self, event_id):
        """
        Mark event as processing

        Arguments:
            event_id -- id of event to be marked
        """

        self.lock.acquire()
        try:
            self.ram.delete(event_id)
            self.persist.mark_as_processing(event_id)
        finally:
            self.lock.release()

    def mark_as_processed(self, event_id):
        """
        Mark event as processing

        Arguments:
            event_id -- id of event to be marked
        """

        self.lock.acquire()
        try:
            self.ram.delete(event_id)
            self.persist.mark_as_processed(event_id)
        finally:
            self.lock.release()

