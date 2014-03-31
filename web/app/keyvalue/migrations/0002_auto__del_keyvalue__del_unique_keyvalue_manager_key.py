# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'KeyValue', fields ['manager', 'key']
        db.delete_unique('keyvalue_keyvalue', ['manager_id', 'key'])

        # Deleting model 'KeyValue'
        db.delete_table('keyvalue_keyvalue')


    def backwards(self, orm):
        # Adding model 'KeyValue'
        db.create_table('keyvalue_keyvalue', (
            ('value', self.gf('django.db.models.fields.CharField')(max_length=8092)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social_auth.Manager'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
        ))
        db.send_create_signal('keyvalue', ['KeyValue'])

        # Adding unique constraint on 'KeyValue', fields ['manager', 'key']
        db.create_unique('keyvalue_keyvalue', ['manager_id', 'key'])


    models = {
        
    }

    complete_apps = ['keyvalue']