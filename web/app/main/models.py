# -*- coding: utf8 -*-
from django.db import models

class Event(models.Model):

    class Meta:
        db_table = 'events' 

    event_time = models.IntegerField()
    data = models.TextField()
    processing = models.BooleanField()
    processed = models.BooleanField()

    processing_timestamp = models.IntegerField()
    processed_timestamp = models.IntegerField()
