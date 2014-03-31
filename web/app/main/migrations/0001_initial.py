# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VkPost'
        db.create_table('main_vkpost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('owner_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=8092)),
            ('from_group', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('event_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('attachments', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('main', ['VkPost'])

        # Adding model 'Event'
        db.create_table('events', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event_time', self.gf('django.db.models.fields.IntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('processing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processing_timestamp', self.gf('django.db.models.fields.IntegerField')()),
            ('processed_timestamp', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main', ['Event'])



    def backwards(self, orm):
        # Deleting model 'VkPost'
        db.delete_table('main_vkpost')
        db.delete_table('events')


    models = {
        'main.vkpost': {
            'Meta': {'object_name': 'VkPost'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'attachments': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'event_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'from_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '8092'})
        }
    }

    complete_apps = ['main']
