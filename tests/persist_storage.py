# -*- coding: utf8 -*-

import unittest
from unittest import TestCase
from scheduler.storage.persist import DBPersistStorage
from random import randint
from time import time

class PersistStorageMixin(object):
    QUANTITY = 100

    def setUp(self):
        self.persist = self.create_persist()
        self.persist.init()

        self.ids = []
        for i in xrange(self.QUANTITY):
            self.ids.append(
                self.persist.add(int(time() + randint(1, 10**6))/60, event_index=i, delay=randint(1, 10**6))
            )

    def test_uniqueness(self):
        self.assertEqual(len(self.ids), self.QUANTITY)
        self.assertEqual(len(filter(lambda x: x > 0, self.ids)), self.QUANTITY)

        ids_map = {}
        for i in xrange(len(self.ids)):
            if ids_map.has_key(self.ids[i]):
                self.fail("Not unique id")
            ids_map[self.ids[i]] = 1

        self.assertEqual(len(ids_map.keys()), self.QUANTITY)

    def test_get(self):
        event = self.persist.get(self.ids[self.QUANTITY / 2])
        self.assertEqual(event.data.event_index, self.QUANTITY / 2)

    def test_update(self):
        event_id = self.ids[self.QUANTITY / 2]
        self.persist.update(event_id, 1, event_index=1, delay=1)
        
        # TODO: !!!! SQLAlchemy caches query results
        event = self.persist.get(event_id)
        self.assertEqual(event.data.event_index, 1)
        self.assertEqual(event.data.delay, 1)
        
    def test_mark_as_processing(self):
        event_id = self.ids[self.QUANTITY / 2]
        self.persist.mark_as_processing(event_id)

    def test_mark_as_processing(self):
        event_id = self.ids[self.QUANTITY / 2]
        self.persist.mark_as_processed(event_id)


    def test_delete(self):
        event_id = self.ids[self.QUANTITY / 2]
        self.persist.delete(event_id)
        self.assertEqual(self.persist.get(event_id), None)

    def test_serialize(self):
        objects = [[1,2,3], {}, u"string", 10.0, 10]
        for obj in objects:
            event_id = self.persist.add(0, obj=obj)

            event_obj = self.persist.get(event_id).data.obj
            self.assertEqual(event_obj, obj)
            self.assertTrue(isinstance(event_obj, obj.__class__))

    def test_all(self):
        counter = 0
        for obj in self.persist.all(yield_per=1, from_time=int(time())/60):
            counter = counter + 1

        self.assertEqual(counter, self.QUANTITY)


class DBStorageCase(PersistStorageMixin, TestCase):

    create_persist = lambda x: DBPersistStorage('sqlite:///:memory:', echo=False)

if __name__ == '__main__':
    unittest.main()
