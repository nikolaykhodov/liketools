# -*- coding: utf-8 -*-

"""
Fast RAM Storage based on red-black binary trees
"""

from scheduler.storage import RAMStorage, AttrDict
from rbtree import rbtree
from bisect import bisect_left, bisect

class RBTreeStorage(RAMStorage):

    def __init__(self):
        """ Constructor """

        # 
        self.by_time = rbtree()
        self.by_id = rbtree()

        self.by_time_cache = None
        # We change this flag after adding or removing event
        self.changed = False

    def _recalc_cache(self):
        """
        Fetch list of keys from by_time tree
        """

        self.by_time_cache = self.by_time.keys()
        self.changed = False

    def add(self, event_id, event_time, **kwargs):
        """ Add event with unique event_id to in-memory high-performance storage. """

        obj = AttrDict(event_id=event_id, event_time=event_time, data=AttrDict(**kwargs))

        events = self.by_time.get(event_time)
        if events is None:
            events = self.by_time[event_time] = []
        events.append(obj)

        self.by_id[event_id] = obj

        self.changed = True

    def delete(self, event_id):
        """
        Delete event from in-memory storage, not from persistent one.
        """

        obj = self.by_id.get(event_id)

        if obj is None:
            return

        self.by_id[event_id] = None
        self.by_time.get(obj.event_time).remove(obj)

        self.changed = True

    def update(self, event_id, event_time=None, **kwargs):
        """
        Update event. kwargs doesn't overwrite event data, it updates data dictionary.
        """

        obj = self.by_id.get(event_id)

        if obj is None:
            return

        if kwargs:
            obj.data.update(kwargs)

        if event_time is not None and obj.event_time != event_time:
            self.by_time.get(obj.event_time).remove(obj)

            events = self.by_time.get(event_time)

            if events is None:
                events = self.by_time[event_time] = []
            events.append(obj)

            obj.event_time = event_time


        self.changed = True

    def get(self, event_id):
        """
        Return event from in-memory storage, not from persistent one.
        """

        obj = self.by_id.get(event_id)
        return obj if obj is not None else None

    def get_events(self, from_event_time=None, to_event_time=None):
        """ Return events which even_time is greater or equal from_event_time and/or less or equal to_event_time """

        if self.changed is True:
            self._recalc_cache()
        
        if len(self.by_time) == 0:
            return []

        right = None
        if to_event_time is not None:
            right = bisect(self.by_time_cache, to_event_time)

            if right == 0:
                return []

            right = right - 1

        left = None
        if from_event_time is not None:
            left = bisect_left(self.by_time_cache, from_event_time)
            if left == len(self.by_time_cache):
                return []

        left_time = self.by_time_cache[left] if left is not None else None
        right_time = self.by_time_cache[right]+1 if right is not None else None

        if left_time == right_time and left_time is not None:
            return [obj for obj in self.by_time[left_time]]
        else:
            objects = []
            for key in self.by_time[left_time:right_time]:
                for obj in self.by_time[key]:
                    objects.append(obj)

            return objects

        
