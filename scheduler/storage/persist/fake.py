# -*- coding: utf8 -*-

"""
Fake persistent storage
"""

from scheduler.storage import PersistStorage

class FakePersistStorage(PersistStorage):

    """
    Fake storage class
    """

    def __init__(self):
        self.max_event_id = 1

    def add(self, event_time, **kwargs):
        """ 
        Save event to persist storage. Return unique ID of object within storage.

        Arguments:
            event_time -- time in minutes since epoch when event will be triggered
            data       -- data associated with event in JSON-encoded format
        """
        self.max_event_id += 1
        return self.max_event_id

    def delete(self, event_id):
        """
        Delete event from persistent storage.
        """
        pass

    def get(self, event_id):
        """
        Retrieve information about event from persistent storage.
        """
        return None

    def update(self, event_id, event_time=None, **kwargs):
        """
        Retrieve information about event from persistent storage.
        """
        pass

    def initiated(self):
        """ Return True if storage is ready. """
        return True

    def init(self):
        """ Prepare storage for work. """
        pass

    def all(self):
        """ Return all events (objects with field id, event_time, data) """
        return []

    def mark_as_processing(self, event_id):
        """ 
        Set event status to processing
        """
        pass


    def mark_as_processed(self, event_id):
        """ 
        Set event status to processed
        """
        pass

