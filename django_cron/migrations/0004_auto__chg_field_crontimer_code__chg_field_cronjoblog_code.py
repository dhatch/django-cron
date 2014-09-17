# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'CronTimer.code'
        db.alter_column('django_cron_crontimer', 'code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150))

        # Changing field 'CronJobLog.code'
        db.alter_column('django_cron_cronjoblog', 'code', self.gf('django.db.models.fields.CharField')(max_length=150))


    def backwards(self, orm):
        
        # Changing field 'CronTimer.code'
        db.alter_column('django_cron_crontimer', 'code', self.gf('django.db.models.fields.CharField')(max_length=64, unique=True))

        # Changing field 'CronJobLog.code'
        db.alter_column('django_cron_cronjoblog', 'code', self.gf('django.db.models.fields.CharField')(max_length=64))


    models = {
        'django_cron.cronjoblog': {
            'Meta': {'object_name': 'CronJobLog'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'ran_at_time': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        'django_cron.crontimer': {
            'Meta': {'object_name': 'CronTimer'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_run_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['django_cron']
