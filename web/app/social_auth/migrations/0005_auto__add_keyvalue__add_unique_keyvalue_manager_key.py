# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'KeyValue'
        db.create_table('social_auth_keyvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social_auth.Manager'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=8092)),
        ))
        db.send_create_signal('social_auth', ['KeyValue'])

        # Adding unique constraint on 'KeyValue', fields ['manager', 'key']
        db.create_unique('social_auth_keyvalue', ['manager_id', 'key'])


    def backwards(self, orm):
        # Removing unique constraint on 'KeyValue', fields ['manager', 'key']
        db.delete_unique('social_auth_keyvalue', ['manager_id', 'key'])

        # Deleting model 'KeyValue'
        db.delete_table('social_auth_keyvalue')


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
        'social_auth.keyvalue': {
            'Meta': {'unique_together': "(('manager', 'key'),)", 'object_name': 'KeyValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social_auth.Manager']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '8092'})
        },
        'social_auth.login': {
            'Meta': {'object_name': 'Login'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social_auth.Manager']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'ua': ('django.db.models.fields.TextField', [], {})
        },
        'social_auth.manager': {
            'Meta': {'unique_together': "(('uid', 'network'),)", 'object_name': 'Manager', '_ormbases': ['auth.User']},
            'access_token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'expires_in': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'uid': ('django.db.models.fields.IntegerField', [], {}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['social_auth']