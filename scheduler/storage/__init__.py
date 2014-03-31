# -*- coding: utf8 -*-

from abc import abstractmethod, ABCMeta

class AttrDict(dict):
    
    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value

class RAMStorage(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def add(self, event_id, event_time, **kwargs):
        """
        Add event with unique event_id to in-memory high-performance storage.

        Arguments:
            event_id   -- unique ID returned by persistent storage
            event_time -- time in minutes since epoch when event will be triggered
            data       -- data associated with event in JSON-encoded format
        """
        pass

    @abstractmethod
    def delete(self, event_id):
        """
        Delete event from in-memory storage, not from persistent one.
        """
        pass

    @abstractmethod
    def update(self, event_id, event_time=None, **kwargs):
        """
        Update event. kwargs doesn't overwrite event data, it updates data dictionary.
        """
        pass

    @abstractmethod
    def get(self, event_id):
        """
        Return event from in-memory storage, not from persistent one.
        """
        pass

    @abstractmethod
    def get_events(self, from_event_time=None, to_event_time=None):
        """
        Return events which trigger times (event_time) are within [from_event_time; to_event_time] range.
        You might specify only one of it.
        """
        pass

class PersistStorage(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def add(self, event_time, **kwargs):
        """ 
        Save event to persist storage. Return unique ID of object within storage.

        Arguments:
            event_time -- time in minutes since epoch when event will be triggered
            data       -- data associated with event in JSON-encoded format
        """
        pass

    @abstractmethod
    def delete(self, event_id):
        """
        Delete event from persistent storage.
        """
        pass

    @abstractmethod
    def get(self, event_id):
        """
        Retrieve information about event from persistent storage.
        """
        pass

    @abstractmethod
    def update(self, event_id, event_time=None, **kwargs):
        """
        Retrieve information about event from persistent storage.
        """
        pass

    @abstractmethod
    def initiated(self):
        """ Return True if storage is ready. """
        return False

    @abstractmethod
    def init(self):
        """ Prepare storage for work. """
        pass

    @abstractmethod
    def all(self, yield_per=1000, from_time=0):
        """ Return all iterable list of events (objects with field id, event_time, data) """
        pass

    @abstractmethod
    def mark_as_processing(self, event_id):
        """ 
        Set event status to processing
        """
        pass

    @abstractmethod
    def mark_as_processed(self, event_id):
        """ 
        Set event status to processed
        """
        pass

