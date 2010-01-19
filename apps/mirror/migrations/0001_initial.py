
from south.db import db
from django.db import models
from mirror.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'LocationMirrorMap'
        db.create_table('mirror_location_mirror_map', (
            ('id', orm['mirror.LocationMirrorMap:id']),
            ('location', orm['mirror.LocationMirrorMap:location']),
            ('mirror', orm['mirror.LocationMirrorMap:mirror']),
            ('active', orm['mirror.LocationMirrorMap:active']),
        ))
        db.send_create_signal('mirror', ['LocationMirrorMap'])
        
        # Adding model 'Mirror'
        db.create_table('mirror_mirrors', (
            ('id', orm['mirror.Mirror:id']),
            ('name', orm['mirror.Mirror:name']),
            ('baseurl', orm['mirror.Mirror:baseurl']),
            ('rating', orm['mirror.Mirror:rating']),
            ('active', orm['mirror.Mirror:active']),
            ('count', orm['mirror.Mirror:count']),
        ))
        db.send_create_signal('mirror', ['Mirror'])
        
        # Adding model 'OS'
        db.create_table('mirror_os', (
            ('id', orm['mirror.OS:id']),
            ('name', orm['mirror.OS:name']),
            ('priority', orm['mirror.OS:priority']),
        ))
        db.send_create_signal('mirror', ['OS'])
        
        # Adding model 'Product'
        db.create_table('mirror_products', (
            ('id', orm['mirror.Product:id']),
            ('name', orm['mirror.Product:name']),
            ('priority', orm['mirror.Product:priority']),
            ('count', orm['mirror.Product:count']),
            ('active', orm['mirror.Product:active']),
            ('checknow', orm['mirror.Product:checknow']),
        ))
        db.send_create_signal('mirror', ['Product'])
        
        # Adding model 'Location'
        db.create_table('mirror_locations', (
            ('id', orm['mirror.Location:id']),
            ('product', orm['mirror.Location:product']),
            ('os', orm['mirror.Location:os']),
            ('path', orm['mirror.Location:path']),
            ('lang', orm['mirror.Location:lang']),
        ))
        db.send_create_signal('mirror', ['Location'])
        
        # Adding ManyToManyField 'Mirror.regions'
        db.create_table('geoip_mirror_region_map', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mirror', models.ForeignKey(orm.Mirror, null=False)),
            ('region', models.ForeignKey(orm['geoip.Region'], null=False))
        ))
        
        # Creating unique_together for [product, os, lang] on Location.
        db.create_unique('mirror_locations', ['product_id', 'os_id', 'lang'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [product, os, lang] on Location.
        db.delete_unique('mirror_locations', ['product_id', 'os_id', 'lang'])
        
        # Deleting model 'LocationMirrorMap'
        db.delete_table('mirror_location_mirror_map')
        
        # Deleting model 'Mirror'
        db.delete_table('mirror_mirrors')
        
        # Deleting model 'OS'
        db.delete_table('mirror_os')
        
        # Deleting model 'Product'
        db.delete_table('mirror_products')
        
        # Deleting model 'Location'
        db.delete_table('mirror_locations')
        
        # Dropping ManyToManyField 'Mirror.regions'
        db.delete_table('geoip_mirror_region_map')
        
    
    
    models = {
        'geoip.region': {
            'Meta': {'db_table': "'geoip_regions'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'throttle': ('django.db.models.fields.IntegerField', [], {})
        },
        'mirror.location': {
            'Meta': {'unique_together': "(('product', 'os', 'lang'),)", 'db_table': "'mirror_locations'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'os': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.OS']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Product']"})
        },
        'mirror.locationmirrormap': {
            'Meta': {'db_table': "'mirror_location_mirror_map'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Location']"}),
            'mirror': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Mirror']"})
        },
        'mirror.mirror': {
            'Meta': {'db_table': "'mirror_mirrors'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'baseurl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'count': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['geoip.Region']"})
        },
        'mirror.os': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'priority': ('django.db.models.fields.IntegerField', [], {})
        },
        'mirror.product': {
            'Meta': {'db_table': "'mirror_products'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'checknow': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }
    
    complete_apps = ['mirror']
