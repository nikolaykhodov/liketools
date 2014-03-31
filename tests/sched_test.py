# -*- coding: utf-8 -*-

from unittest import TestCase
from scheduler.core import Scheduler
from scheduler.storage.ram import SimpleListStorage, RBTreeStorage
from scheduler.storage.persist import DBPersistStorage
from time import time
from random import randint
from datetime import datetime

class PersistMixin(object):

    DB_CONNECTION = 'sqlite:///:memory:'

    def create_persist(self):
        persist = DBPersistStorage(self.DB_CONNECTION)
        persist.init()

        return persist

    def create_ram(self):
        return RBTreeStorage()

class BasicFunctionTestCase(PersistMixin, TestCase):

    def setUp(self):
        self.ram = self.create_ram()
        self.persist = self.create_persist()
        self.scheduler = Scheduler(ram_storage=self.ram, persist_storage=self.persist)

    def test_add(self):
        event_id = self.scheduler.add(delay_time=1.0, foobar=1)
        self.assertGreater(event_id, 0)

    def test_delete(self):
        event_id = self.scheduler.add(delay_time=1.0, foobar=1)
        self.scheduler.delete(event_id)
        self.assertEqual(self.ram.get(event_id), None)

class RestoreTestCase(PersistMixin, TestCase):

    N = 100

    def setUp(self):
        self.ram = self.create_ram()
        self.persist = self.create_persist()
        self.scheduler1 = Scheduler(ram_storage=self.create_ram(), persist_storage=self.persist)

        self.trigger_time = int(time() + 600)
        for i in xrange(self.N):
            self.scheduler1.add(trigger_time=self.trigger_time, ev_index=i, ev_data=[{'%s' % i: i}])

        self.scheduler2 = Scheduler(ram_storage=self.create_ram(), persist_storage=self.persist)

    def test_restore(self):
        self.scheduler2.restore()
        events = self.scheduler2.get_events(self.trigger_time)
        self.assertEqual(len(events), self.N)
        for event in events:
            self.assertEqual(event.data.ev_data[0][str(event.data.ev_index)], event.data.ev_index)

class SchedulerTestCase(PersistMixin, TestCase):

    ram_storages = [RBTreeStorage, SimpleListStorage]

    def generate_schedule(self, duration, events, current_time=None):
        #current_time = int(time()) / 60 * 60
        if current_time == 0:
            current_time = int(time())
        delays = {}

        for i in xrange(events):
            delay = randint(1, duration)
            delay_key = str(delay)

            if not delays.has_key(str(delay)):
                delays[delay_key] = []

            delays[delay_key].append(dict(key=i))

        schedule = [[0, []]]
        for i in xrange(1,duration):
            schedule.append([0, []])
            if delays.has_key(str(i)):
                schedule[i] = (current_time + i * 60.0, delays[str(i)])

        return schedule



    def do_test(self, duration, events):
        current_time = int(time())
        schedule = self.generate_schedule(duration, events, current_time=current_time)

        scheduler = Scheduler(
            ram_storage=self.ram_storages[randint(0,len(self.ram_storages)-1)](), 
            persist_storage=self.create_persist()
        ) 

        for event_time, events in schedule:
            if event_time == 0:
                continue
            for event in events:
                scheduler.add(trigger_time=event_time, key=event['key'])

        for i in xrange(0, duration):
           events = scheduler.get_events(current_time + i * 60.0)
           events = [ev.data for ev in events]
           if events != schedule[i][1]:
               print "fail tick = ", i
               events = scheduler.get_events(current_time + i * 60.0)
           self.assertEqual(events, schedule[i][1])

    def do_tests(self, max_duration, max_events, ticks):
        print "Start fuzz testing..."
        for i in xrange(ticks):
            duration = randint(1, max_duration)
            events = randint(1, max_events)

            print "%s iteration of fuzz testing (duration=%s, events=%s)..." % ((i+1), duration, events)

            self.do_test(duration, events)
       
    def test_synthetic(self):
        self.do_test(1, 273)

    def test_dense(self):
        self.do_tests(120, 1000, 20)

    def test_sparse(self):
        self.do_tests(3600, 500, 20)

        
class DateTimeAwarenessCase(PersistMixin, TestCase):
    
    def setUp(self):
        self.ram = self.create_ram()
        self.persist = self.create_persist()
        self.scheduler = Scheduler(ram_storage=self.ram, persist_storage=self.persist)

    def test_convert(self):

        dt1 = datetime.now()
        dt2 = datetime.utcnow()

        delta1 = self.scheduler.timestamp2dt(self.scheduler.dt2timestamp(dt1)) - dt1
        delta2 = self.scheduler.timestamp2dt(self.scheduler.dt2timestamp(dt2)) - dt2

        self.assertLess(delta1.total_seconds(), 1.0)
        self.assertLess(delta2.total_seconds(), 1.0)
