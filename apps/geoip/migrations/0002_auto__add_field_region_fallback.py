# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Region.fallback'
        db.add_column('geoip_regions', 'fallback', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geoip.Region'], null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Region.fallback'
        db.delete_column('geoip_regions', 'fallback_id')


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
