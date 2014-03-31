# -*- coding: utf8 -*-

import unittest
from unittest import TestCase
from scheduler.storage.ram import SimpleListStorage, RBTreeStorage
from random import randint

class RAMStorageMixin(object):

    class_to_be_tested = None

    def setUp(self):
        self.event_times = [2, 8, 13, 20, 28, 31, 34, 44, 54, 59]
        self.events = [(event_id, self.event_times[event_id]) for event_id in xrange(len(self.event_times))]
        self.ram = self.class_to_be_tested()

        try:
            for event_id, event_time in self.events:
                self.ram.add(event_id=event_id, event_time=event_time, ev_id=event_id, ev_time=event_time)
        except Exception, ex:
            self.fail("Fail to add event in %s class" % self.testing_class)


    def test_get(self):
        self.assertEqual(self.ram.get(-1), None)
        self.assertEqual(self.ram.get(100), None)
        # All events must be in RAM
        for event_id, event_time in self.events:
           self.assertEqual(self.ram.get(event_id).data.ev_id, event_id)
           self.assertEqual(self.ram.get(event_id).data.ev_time, event_time)

    def test_update(self):
        event_id, event_time = self.events[randint(0, len(self.events)-1)]

        # Update event data
        self.ram.update(event_id, None, ev_id=0, new_data=1)
        self.assertEqual(self.ram.get(event_id).data.ev_id, 0)
        self.assertEqual(self.ram.get(event_id).data.new_data, 1)

        # Update event time and event data
        self.ram.update(event_id, 1, ev_id=event_id, ev_time=None)
        self.assertEqual(self.ram.get(event_id).data.ev_id, event_id)
        self.assertEqual(self.ram.get(event_id).data.ev_time, None)

        # Event with new event_time must be in get_events() result
        events = self.ram.get_events(from_event_time=1, to_event_time=1)
        self.assertGreaterEqual(len(map(lambda x: x.ev_id==event_id, events)), 1)

    def test_delete(self):
        self.ram.delete(1)
        self.assertEqual(self.ram.get(1), None)

    def test_get_events(self):
        def get_events_time(func):
            def wrapper(*args, **kwargs):
                return [event.data.ev_time for event in func(*args, **kwargs)]
            return wrapper

        self.ram.get_events = get_events_time(self.ram.get_events)
        self.assertEqual(self.ram.get_events(), [ev[1] for ev in self.events])
        self.assertEqual(self.ram.get_events(12,21), [13,20])
        self.assertEqual(self.ram.get_events(13,20), [13,20])

        self.assertEqual(self.ram.get_events(to_event_time=1), [])
        self.assertEqual(self.ram.get_events(1,3), [2])
        self.assertEqual(self.ram.get_events(31,44), [31,34,44])
        self.assertEqual(self.ram.get_events(55), [59])
        self.assertEqual(self.ram.get_events(None,14), [2,8,13])
        self.assertEqual(self.ram.get_events(9,32), [13,20,28,31])
        self.assertEqual(self.ram.get_events(34,34), [34])


class SimpleListCase(RAMStorageMixin, TestCase):

    class_to_be_tested = SimpleListStorage

class RBTreeCase(RAMStorageMixin, TestCase):

    class_to_be_tested = RBTreeStorage

if __name__ == '__main__':
    unittest.main()
