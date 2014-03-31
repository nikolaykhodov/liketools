# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Group.alias'
        db.add_column('manager_group', 'alias',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128),
                      keep_default=False)


        # Renaming column for 'Group.manager' to match new field type.
        db.rename_column('manager_group', 'manager', 'manager_id')
        # Changing field 'Group.manager'
        db.alter_column('manager_group', 'manager_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social_auth.Manager']))
        # Adding index on 'Group', fields ['manager']
        db.create_index('manager_group', ['manager_id'])

        # Adding index on 'Group', fields ['gid']
        db.create_index('manager_group', ['gid'])

        # Adding unique constraint on 'Group', fields ['manager', 'gid']
        db.create_unique('manager_group', ['manager_id', 'gid'])


    def backwards(self, orm):
        # Removing unique constraint on 'Group', fields ['manager', 'gid']
        db.delete_unique('manager_group', ['manager_id', 'gid'])

        # Removing index on 'Group', fields ['gid']
        db.delete_index('manager_group', ['gid'])

        # Removing index on 'Group', fields ['manager']
        db.delete_index('manager_group', ['manager_id'])

        # Deleting field 'Group.alias'
        db.delete_column('manager_group', 'alias')


        # Renaming column for 'Group.manager' to match new field type.
        db.rename_column('manager_group', 'manager_id', 'manager')
        # Changing field 'Group.manager'
        db.alter_column('manager_group', 'manager', self.gf('django.db.models.fields.PositiveIntegerField')())

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'manager.group': {
            'Meta': {'unique_together': "(('manager', 'gid'),)", 'object_name': 'Group'},
            'alias': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'gid': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social_auth.Manager']"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '192'})
        },
        'social_auth.manager': {
            'Meta': {'unique_together': "(('uid', 'network'),)", 'object_name': 'Manager', '_ormbases': ['auth.User']},
            'network': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'uid': ('django.db.models.fields.IntegerField', [], {}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['manager']