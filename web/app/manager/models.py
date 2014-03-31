# -*- coding: utf8 -*-
from django.db import models
from jsonfield import JSONField
from social_auth.models import Manager

import json
import time
import pytz

class Group(models.Model):

    class Meta:
        unique_together = (('manager', 'gid'), )

    manager = models.ForeignKey(Manager)
    gid = models.PositiveIntegerField(blank=False, db_index=True)
    name = models.CharField(max_length=192, default='')
    alias = models.CharField(max_length=128, default='')


class Account(models.Model):

    class Meta:
        unique_together = (('manager', 'name'), )

    manager = models.ForeignKey(Manager)
    name = models.CharField(max_length=128)
    access_token = models.CharField(max_length=512, blank=True)

class Campaign(models.Model):

    """ Модель рекламных кампаний для группировки постов """

    class Meta:
        unique_together = (('manager', 'name'), )

    manager = models.ForeignKey(Manager)
    name = models.CharField(max_length=128)

    def get_delete_messages(self):
        """
        Возвращает массив сообщения в планировщик для удаления всех постов кампании
        """

        messages = []

        posts = VkPost.objects.filter(campaign=self)
        for post in posts:
            messages.extend(post.get_delete_messages())

        return messages

class VkPost(models.Model):

    """ Модуль поста в ВК """

    class Meta:
        db_table = 'main_vkpost'

    STATUS_CHOICES = (
        ('waiting', 'waiting'),
        ('posted', 'posted'),
        ('with_errors', 'with_errors')
    )


    campaign = models.ForeignKey(Campaign)
    access_token = models.CharField(max_length=128)
    when_to_post = models.DateTimeField(default='1970-01-01 00:00')
    when_to_delete = models.DateTimeField(default='1970-01-01 00:00', null=True)
    # Comma separated list of owner_ids
    owner_ids = models.CommaSeparatedIntegerField(max_length=1024, default='')
    text = models.CharField(max_length=8092, default='')
    from_group = models.BooleanField(default=False)
    attachments = models.CharField(max_length=1024, default='')

    editor_data = models.CharField(max_length=8092, default='')

    links = JSONField(default=[])

    status = models.CharField(max_length=32, default='waiting', db_index=True, choices=STATUS_CHOICES)

    def get_delete_messages(self):
        """
        Возвращает сообщения в планировщик для удаления постов из очереди
        """
        # Подготовить сообщения для очистки очереди
        messages = []
        for event in VkPostEvent.objects.filter(post=self):
            messages.append(dict(
                action='delete',
                event_id=event.event_id
            ))

        return messages

    def get_scheduler_data(self):
        """
        Возвращает данные для планировщика: (время размещения, время удаления, словарь с базовыми данными для отсылки в постер)
        """

        posting_time = int(time.mktime(self.when_to_post.astimezone(pytz.utc).timetuple()))
        delete_time = None
        if self.when_to_delete:
            delete_time = int(time.mktime(self.when_to_delete.astimezone(pytz.utc).timetuple()))

        return (posting_time, delete_time, dict(
            lt_self_id=self.pk,
            text=self.text,
            owner_ids=self.owner_ids or "",
            from_group=self.from_group,
            attachments=self.attachments,
            access_token=self.access_token
        ))

    def delete(self, *args, **kwargs):
        """
        Удаляет пост и возвращает сообщение для отправки в планировщик 
        """

        # Удалить все события и сам пост
        VkPostEvent.objects.filter(post=self).delete()
        super(VkPost, self).delete(*args, **kwargs)

        return self.get_delete_messages()

    def get_vk_posts(self):
        """
        Возвращает информацию о размещенных постах в ВК 
        [{owner_id: <int>, log: <str>, post_id: <int>}, ...]

        """
        posts = []

        owner_ids = json.loads(self.owner_ids)
        if not isinstance(owner_ids, list):
            owner_ids = [owner_ids]
                    
        for owner_id in owner_ids:
            owner_id = str(owner_id)
            posts.append(dict(
                owner_id=owner_id,
                log=self.links[owner_id].get('log'),
                post_id=self.links[owner_id].get('post_id'),
                timestamp=self.links[owner_id].get('timestamp')
            ))

        return posts

class VkPostEvent(models.Model):
    
    """ Соответствие постов в ВК и событий с ними """

    class Meta:
        unique_together = (('post', 'event_id'), )

    TYPE_CHOICES = (
       ('delete', 'delete'),
       ('add', 'add')
    )
    post = models.ForeignKey(VkPost)
    event_id = models.PositiveIntegerField(db_index=True)
    event_type = models.CharField(max_length=16, default='', choices=TYPE_CHOICES)
