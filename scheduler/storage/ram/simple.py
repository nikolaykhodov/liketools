# -*- coding: utf8 -*-

"""
RAM storage class based on simple linear list.
"""

from scheduler.storage import RAMStorage, AttrDict

class SimpleListStorage(RAMStorage):

    """
    RAM storage class.
    """

    def __init__(self):
        self.objects = []

    def _find_index(self, event_id):       
        index = 0

        for obj in self.objects:
            if obj.event_id == event_id:
                return index

            index += 1

        return None

    def add(self, event_id, event_time, **kwargs):
        """ Add event with unique event_id to in-memory high-performance storage. """
        self.objects.append(AttrDict(event_id=event_id, event_time=event_time, data=AttrDict(**kwargs)))

    def delete(self, event_id):
        """
        Delete event from in-memory storage, not from persistent one.
        """
        index = self._find_index(event_id)
        if index is not None:
            del self.objects[index]

    def update(self, event_id, event_time=None, **kwargs):
        """
        Update event. kwargs doesn't overwrite event data, it updates data dictionary.
        """
        index = self._find_index(event_id)

        if index is None:
            return

        obj = self.objects[index]

        if event_time is not None:
            obj.event_time = event_time

        if kwargs:
            obj.data.update(kwargs)

    def get(self, event_id):
        """
        Return event from in-memory storage, not from persistent one.
        """
        index = self._find_index(event_id)
        return self.objects[index] if index is not None else None

    def get_events(self, from_event_time=None, to_event_time=None):
        """ Return events which even_time is greater or equal from_event_time and/or less or equal to_event_time """
        objects = []

        for obj in self.objects:
            if from_event_time:
                if obj.event_time < from_event_time:
                    continue

            if to_event_time:
                if obj.event_time > to_event_time:
                    continue

            objects.append(obj)

        return objects


