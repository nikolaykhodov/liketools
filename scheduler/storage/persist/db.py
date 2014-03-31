# -*- coding: utf8 -*-

"""
Persistent storages which store data in DB using SQLAlchemy
"""

from scheduler.storage import PersistStorage, AttrDict
from sqlalchemy.types import PickleType
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from time import mktime

Base = declarative_base()

class TextPickleType(PickleType):
    """
    Implementation of JSON picker for event data storing.
    """

    impl = Text

class Event(Base):
    """ Map class for storing events in DB """

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    event_time = Column(Integer, index=True)
    data = Column(TextPickleType(pickler=json))
    processing = Column(Integer, index=True, default=0)
    processing_timestamp = Column(Integer, default=0)
    processed = Column(Integer, index=True, default=0)
    processed_timestamp = Column(Integer, default=0)

    def __init__(self, event_time, **kwargs):
        self.event_time = event_time
        self.data = kwargs

    def __repr__(self):
        return "<Event(event_time=%s')>" % self.event_time

class DBPersistStorage(PersistStorage):

    """
    Persistent storage class based on DB
    """

    def __init__(self, connection, **kwargs):
        """
        Constructor
        
        Arguments:
            connection -- SQLAlchemy-style string with data for accessing DB
                          <db_provider>://<username>:<password>@<host>/<db_name>
        """

        self.engine = create_engine(connection, **kwargs)
        self.Session = sessionmaker(bind=self.engine, autocommit=True)

    def init(self):
        """ Prepare storage for work. """
        Base.metadata.create_all(self.engine)

    def initiated(self):
        """ Return True if storage is ready. """
        inspector = Inspector.from_engine(self.engine)
        return "events" in inspector.get_table_names()

    def add(self, event_time, **kwargs):
        """ 
        Save event to persist storage. Return unique ID of object within storage.

        Arguments:
            event_time -- time in minutes since epoch when event will be triggered
            data       -- data associated with event in JSON-encoded format
        """
        event = Event(event_time, **kwargs)

        session = self.Session()
        session.begin()
        try:
            session.add(event)
            session.commit()
            return event.id
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def update(self, event_id, event_time=None, **kwargs):
        """
        Retrieve information about event from persistent storage.
        """
        session = self.Session()
        event = session.query(Event).get(event_id)

        session.begin()
        try:
            if event_time != None:
                event.event_time = event_time
            
            new_data = event.data.copy()
            new_data.update(kwargs)
            event.data = new_data

            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    def delete(self, event_id):
        """
        Delete event from persistent storage.
        """
        session = self.Session()

        session.begin()
        try:
            session.query(Event).filter_by(id=event_id).delete()
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        
    def get(self, event_id):
        """
        Retrieve information about event from persistent storage.
        """
        session = self.Session()
        try:
            event = session.query(Event).filter_by(id=event_id).first()
            return AttrDict(
                event_id=event.id,
                event_time=event.event_time,
                data = AttrDict(event.data)
            ) if event is not None else None
        finally:
            session.close()

    def all(self, yield_per=1000, from_time=0):
        """ Return all iterable list of events (objects with field id, event_time, data) """
        session = self.Session()
        return session.query(Event). \
                filter(Event.event_time >= from_time, Event.processing == 0, Event.processed == 0).yield_per(yield_per)

    def mark_as_processing(self, event_id):
        """ 
        Set event status to processing
        """

        session = self.Session()
        event = session.query(Event).get(event_id)

        session.begin()
        try:
            event.processing = 1
            event.processing_timestamp = mktime(datetime.utcnow().timetuple())
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    def mark_as_processed(self, event_id):
        """ 
        Set event status to processed
        """

        session = self.Session()
        event = session.query(Event).get(event_id)

        session.begin()
        try:
            event.processed = 1
            event.processed_timestamp = mktime(datetime.utcnow().timetuple())
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
