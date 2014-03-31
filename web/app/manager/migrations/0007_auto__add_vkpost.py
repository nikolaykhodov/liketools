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
            ('when_to_post', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00')),
            ('when_to_delete', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00', null=True)),
            ('owner_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('text', self.gf('django.db.models.fields.CharField')(default='', max_length=8092)),
            ('from_group', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attachments', self.gf('django.db.models.fields.CharField')(default='', max_length=1024)),
            ('event_id', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('link', self.gf('django.db.models.fields.CharField')(default='', max_length=1024)),
            ('link_timestamp', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00')),
            ('log', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('manager', ['VkPost'])


    def backwards(self, orm):
        # Deleting model 'VkPost'
        db.delete_table('main_vkpost')


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
        'manager.account': {
            'Meta': {'unique_together': "(('manager', 'name'),)", 'object_name': 'Account'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social_auth.Manager']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'manager.campaign': {
            'Meta': {'unique_together': "(('manager', 'name'),)", 'object_name': 'Campaign'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social_auth.Manager']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'manager.group': {
            'Meta': {'unique_together': "(('manager', 'gid'),)", 'object_name': 'Group'},
            'alias': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'gid': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social_auth.Manager']"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '192'})
        },
        'manager.vkpost': {
            'Meta': {'object_name': 'VkPost', 'db_table': "'main_vkpost'"},
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
            'when_to_delete': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00'", 'null': 'True'}),
            'when_to_post': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00'"})
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

    complete_apps = ['manager']