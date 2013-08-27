# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProductAlias'
        db.create_table('mirror_aliases', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('related_product', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('mirror', ['ProductAlias'])

        # Adding field 'LocationMirrorMap.healthy'
        db.add_column('mirror_location_mirror_map', 'healthy',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Product.ssl_only'
        db.add_column('mirror_products', 'ssl_only',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ProductAlias'
        db.delete_table('mirror_aliases')

        # Deleting field 'LocationMirrorMap.healthy'
        db.delete_column('mirror_location_mirror_map', 'healthy')

        # Deleting field 'Product.ssl_only'
        db.delete_column('mirror_products', 'ssl_only')


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
        'geoip.region': {
            'Meta': {'object_name': 'Region', 'db_table': "'geoip_regions'"},
            'fallback': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geoip.Region']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prevent_global_fallback': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        'mirror.locationmirrorlanguageexception': {
            'Meta': {'unique_together': "(('lmm', 'lang'),)", 'object_name': 'LocationMirrorLanguageException', 'db_table': "'mirror_lmm_lang_exceptions'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "'language'"}),
            'lmm': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lang_exceptions'", 'db_column': "'location_mirror_map_id'", 'to': "orm['mirror.LocationMirrorMap']"})
        },
        'mirror.locationmirrormap': {
            'Meta': {'object_name': 'LocationMirrorMap', 'db_table': "'mirror_location_mirror_map'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'healthy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Location']"}),
            'mirror': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirror.Mirror']"})
        },
        'mirror.mirror': {
            'Meta': {'object_name': 'Mirror', 'db_table': "'mirror_mirrors'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'baseurl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['geoip.Region']", 'db_table': "'geoip_mirror_region_map'", 'symmetrical': 'False'})
        },
        'mirror.os': {
            'Meta': {'object_name': 'OS'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mirror.product': {
            'Meta': {'object_name': 'Product', 'db_table': "'mirror_products'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'checknow': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'count': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'ssl_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'mirror.productalias': {
            'Meta': {'object_name': 'ProductAlias', 'db_table': "'mirror_aliases'"},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'related_product': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'mirror.productlanguage': {
            'Meta': {'unique_together': "(('product', 'lang'),)", 'object_name': 'ProductLanguage', 'db_table': "'mirror_product_langs'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "'language'"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'to': "orm['mirror.Product']"})
        }
    }

    complete_apps = ['mirror']