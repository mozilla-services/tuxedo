# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Country'
        db.create_table('geoip_country_to_region', (
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=2, primary_key=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geoip.Region'], null=True)),
            ('country_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('continent', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('geoip', ['Country'])

        # Adding model 'IPBlock'
        db.create_table('geoip_ip_to_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_start', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=0)),
            ('ip_end', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=0)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geoip.Country'], db_column='country_code')),
        ))
        db.send_create_signal('geoip', ['IPBlock'])

        # Adding model 'Region'
        db.create_table('geoip_regions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('throttle', self.gf('django.db.models.fields.IntegerField')()),
            ('fallback', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geoip.Region'], null=True)),
        ))
        db.send_create_signal('geoip', ['Region'])


    def backwards(self, orm):
        
        # Deleting model 'Country'
        db.delete_table('geoip_country_to_region')

        # Deleting model 'IPBlock'
        db.delete_table('geoip_ip_to_country')

        # Deleting model 'Region'
        db.delete_table('geoip_regions')


    models = {
        'geoip.country': {
            'Meta': {'object_name': 'Country', 'db_table': "'geoip_country_to_region'"},
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geoip.Region']", 'null': 'True'})
        },
        'geoip.ipblock': {
            'Meta': {'object_name': 'IPBlock', 'db_table': "'geoip_ip_to_country'"},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geoip.Country']", 'db_column': "'country_code'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_end': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '0'}),
            'ip_start': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '0'})
        },
        'geoip.region': {
            'Meta': {'object_name': 'Region', 'db_table': "'geoip_regions'"},
            'fallback': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geoip.Region']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'throttle': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['geoip']
