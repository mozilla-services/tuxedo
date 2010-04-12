# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Mirror'
        db.create_table('mirror_mirrors', (
            ('count', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=0, db_index=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('baseurl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('mirror', ['Mirror'])

        # Adding M2M table for field regions on 'Mirror'
        db.create_table('geoip_mirror_region_map', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mirror', models.ForeignKey(orm['mirror.mirror'], null=False)),
            ('region', models.ForeignKey(orm['geoip.region'], null=False))
        ))
        db.create_unique('geoip_mirror_region_map', ['mirror_id', 'region_id'])

        # Adding model 'OS'
        db.create_table('mirror_os', (
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('mirror', ['OS'])

        # Adding model 'Product'
        db.create_table('mirror_products', (
            ('count', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=0)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('checknow', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('mirror', ['Product'])

        # Adding model 'ProductLanguages'
        db.create_table('mirror_product_langs', (
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=30, db_column='language')),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', to=orm['mirror.Product'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('mirror', ['ProductLanguages'])

        # Adding unique constraint on 'ProductLanguages', fields ['product', 'lang']
        db.create_unique('mirror_product_langs', ['product_id', 'language'])

        # Adding model 'Location'
        db.create_table('mirror_locations', (
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirror.Product'])),
            ('os', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirror.OS'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('mirror', ['Location'])

        # Adding unique constraint on 'Location', fields ['product', 'os']
        db.create_unique('mirror_locations', ['product_id', 'os_id'])

        # Adding model 'LocationMirrorMap'
        db.create_table('mirror_location_mirror_map', (
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('mirror', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirror.Mirror'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirror.Location'])),
        ))
        db.send_create_signal('mirror', ['LocationMirrorMap'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Mirror'
        db.delete_table('mirror_mirrors')

        # Removing M2M table for field regions on 'Mirror'
        db.delete_table('geoip_mirror_region_map')

        # Deleting model 'OS'
        db.delete_table('mirror_os')

        # Deleting model 'Product'
        db.delete_table('mirror_products')

        # Deleting model 'ProductLanguages'
        db.delete_table('mirror_product_langs')

        # Removing unique constraint on 'ProductLanguages', fields ['product', 'lang']
        db.delete_unique('mirror_product_langs', ['product_id', 'language'])

        # Deleting model 'Location'
        db.delete_table('mirror_locations')

        # Removing unique constraint on 'Location', fields ['product', 'os']
        db.delete_unique('mirror_locations', ['product_id', 'os_id'])

        # Deleting model 'LocationMirrorMap'
        db.delete_table('mirror_location_mirror_map')
    
    
    models = {
        'geoip.region': {
            'Meta': {'object_name': 'Region', 'db_table': "'geoip_regions'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'throttle': ('django.db.models.fields.IntegerField', [], {})
        },
        'mirror.location': {
            'Meta': {'unique_together': "(('product', 'os'),)", 'object_name': 'Location', 'db_table': "'mirror_locations'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'os': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.OS']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Product']"})
        },
        'mirror.locationmirrormap': {
            'Meta': {'object_name': 'LocationMirrorMap', 'db_table': "'mirror_location_mirror_map'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Location']"}),
            'mirror': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Mirror']"})
        },
        'mirror.mirror': {
            'Meta': {'object_name': 'Mirror', 'db_table': "'mirror_mirrors'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'baseurl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'count': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['geoip.Region']", 'db_table': "'geoip_mirror_region_map'"})
        },
        'mirror.os': {
            'Meta': {'object_name': 'OS'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mirror.product': {
            'Meta': {'object_name': 'Product', 'db_table': "'mirror_products'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'checknow': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'mirror.productlanguages': {
            'Meta': {'unique_together': "(('product', 'lang'),)", 'object_name': 'ProductLanguages', 'db_table': "'mirror_product_langs'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "'language'"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'to': "orm['mirror.Product']"})
        }
    }
    
    complete_apps = ['mirror']
