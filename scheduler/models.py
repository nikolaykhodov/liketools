# -*- coding: utf8 -*-
"""
Scheduler DB models 
"""

from sqlalchemy import Column, Integer, Text, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import PickleType

import json

Base = declarative_base()

class TextPickleType(PickleType):
    """
    Implementation of JSON picker for event data storing.
    """

    impl = Text


class VkPost(Base):
    """ Map class for storing posts in DB """

    __tablename__ = 'main_vkpost'

    id = Column(Integer, primary_key=True)
    access_token = Column(String(128))
    when_to_post = Column(DateTime)
    when_to_delete = Column(DateTime)
    text = Column(String(8192), default='')
    from_group = Column(Boolean)
    attachments = Column(String(1024), default='')

    links = Column(TextPickleType(pickler=json))
    editor_data = Column(String(8092), default='{}')
    status = Column(String(32), default='waiting', index=True)

    def __repr__(self):
        return "<VkPost(event_time=%s')>" % self.event_time

class VkPostEvent(Base):

    __tablename__ = 'manager_vkpostevent'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    event_id = Column(Integer)
    event_type = Column(String(16))
