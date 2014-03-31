# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Group'
        db.create_table('manager_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manager', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('gid', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=192)),
        ))
        db.send_create_signal('manager', ['Group'])


    def backwards(self, orm):
        # Deleting model 'Group'
        db.delete_table('manager_group')


    models = {
        'manager.group': {
            'Meta': {'object_name': 'Group'},
            'gid': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '192'})
        }
    }

    complete_apps = ['manager']