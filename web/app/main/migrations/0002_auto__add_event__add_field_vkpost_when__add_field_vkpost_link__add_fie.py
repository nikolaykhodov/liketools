# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'VkPost.when'
        db.add_column('main_vkpost', 'when',
                      self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00'),
                      keep_default=False)

        # Adding field 'VkPost.link'
        db.add_column('main_vkpost', 'link',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1024),
                      keep_default=False)

        # Adding field 'VkPost.line_timestamp'
        db.add_column('main_vkpost', 'line_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00'),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table('events')

        # Deleting field 'VkPost.when'
        db.delete_column('main_vkpost', 'when')

        # Deleting field 'VkPost.link'
        db.delete_column('main_vkpost', 'link')

        # Deleting field 'VkPost.line_timestamp'
        db.delete_column('main_vkpost', 'line_timestamp')


    models = {
        'main.event': {
            'Meta': {'object_name': 'Event', 'db_table': "'events'"},
            'data': ('django.db.models.fields.TextField', [], {}),
            'event_time': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processed_timestamp': ('django.db.models.fields.IntegerField', [], {}),
            'processing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processing_timestamp': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.vkpost': {
            'Meta': {'object_name': 'VkPost'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'attachments': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'event_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'from_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024'}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '8092'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'default': '0'})
        }
    }

    complete_apps = ['main']
