# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'VkPost.status'
        db.add_column('main_vkpost', 'status',
                      self.gf('django.db.models.fields.CharField')(default='waiting', max_length=32, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'VkPost.status'
        db.delete_column('main_vkpost', 'status')


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
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manager.Campaign']"}),
            'editor_data': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8092'}),
            'from_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'links': ('jsonfield.fields.JSONField', [], {'default': '[]'}),
            'owner_ids': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '1024'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'waiting'", 'max_length': '32', 'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8092'}),
            'when_to_delete': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00'", 'null': 'True'}),
            'when_to_post': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00'"})
        },
        'manager.vkpostevent': {
            'Meta': {'unique_together': "(('post', 'event_id'),)", 'object_name': 'VkPostEvent'},
            'event_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manager.VkPost']"})
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