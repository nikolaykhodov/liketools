# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'VkPost.when'
        db.delete_column('main_vkpost', 'when')

        # Adding field 'VkPost.when_to_post'
        db.add_column('main_vkpost', 'when_to_post',
                      self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00'),
                      keep_default=False)

        # Adding field 'VkPost.when_to_delete'
        db.add_column('main_vkpost', 'when_to_delete',
                      self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'VkPost.when'
        db.add_column('main_vkpost', 'when',
                      self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00'),
                      keep_default=False)

        # Deleting field 'VkPost.when_to_post'
        db.delete_column('main_vkpost', 'when_to_post')

        # Deleting field 'VkPost.when_to_delete'
        db.delete_column('main_vkpost', 'when_to_delete')


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
            'attachments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024'}),
            'event_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'from_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024'}),
            'link_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00'"}),
            'log': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8092'}),
            'when_to_delete': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00'"}),
            'when_to_post': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00'"})
        }
    }

    complete_apps = ['main']
