# -*- coding: utf8 -*-

from scheduler.models import VkPostEvent
import logging

def add_event_id(session, lt_post_id, event_id, event_type=''):
    """
    Прописывает у поста (id=lt_post_id) значение колонки event_id

    Параметры:
        -- session - текущая сессия работы с базой данных
        -- lt_post_id - номер поста, соответствующему событию
        -- event_id - номер события
        -- тип события - тип события (берется из параметра data['action'] присланного в планировщик сообщения
    """

    postevent = VkPostEvent()
    session.begin()
    try:
        postevent.post_id = lt_post_id
        postevent.event_id = event_id
        postevent.event_type = event_type
        session.add(postevent)
        session.commit()
    except Exception, exc:
        logging.error("Exception:\n%s", exc)
        session.rollback()
    finally:
        session.close()
        
