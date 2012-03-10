# encoding: utf-8
import re
from south.v2 import DataMigration


def to_camel_case(name, separator='_'):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1%s\2' % separator, name)
    return re.sub('([a-z0-9])([A-Z])', r'\1%s\2' % separator, s1).lower()


class Migration(DataMigration):

    def forwards(self, orm):
	"Write your forwards methods here."
	apps = {
	    'mirror': ['Mirror', 'Product', 'ProductLanguage', 'Location'],
	    'geoip': ['Country', 'Region']
	}

	api_perms = []
	volunteer_perms = []
	for app, models in apps.iteritems():
	    for model in models:
		ct, created = orm['contenttypes.ContentType'].objects.get_or_create(
		    model=model.lower(), app_label=app.lower(), name=model)
		for permission in ['add', 'change', 'delete']:
		    codename = '%s_%s' % (permission, to_camel_case(model))
		    name = u'Can %s %s' % (permission, to_camel_case(model, ' '))
		    perm, created = orm['auth.permission'].objects.get_or_create(
			content_type=ct, codename=codename, name=name)

		    if model in ['Product', 'ProductLanguage', 'Location']:
			api_perms.append(perm)
		    if model in ['Mirror', 'Country', 'Region']:
			volunteer_perms.append(perm)

	ct, created = orm['contenttypes.ContentType'].objects.get_or_create(
	    model='location', app_label='mirror')
	perm, created = orm['auth.permission'].objects.get_or_create(
	    content_type=ct, codename='view_uptake', name=u'Can view mirror uptake')
	api_perms.append(perm)

	group, created = orm['auth.group'].objects.get_or_create(name='API access')
	group.permissions.add(*api_perms)
	staff_users = orm['auth.user'].objects.filter(is_staff=True)
	group.user_set.add(*staff_users)

	group, created = orm['auth.group'].objects.get_or_create(name='Volunteer admins')
	group.permissions.add(*volunteer_perms)

    def backwards(self, orm):
	"Write your backwards methods here."

    models = {
	'auth.group': {
	    'Meta': {'object_name': 'Group'},
	    'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
	    'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
	    'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
	},
	'auth.message': {
	    'Meta': {'object_name': 'Message'},
	    'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
	    'message': ('django.db.models.fields.TextField', [], {}),
	    'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_message_set'", 'to': "orm['auth.User']"})
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
	'mirror.locationmirrorlanguageexception': {
	    'Meta': {'unique_together': "(('lmm', 'lang'),)", 'object_name': 'LocationMirrorLanguageException', 'db_table': "'mirror_lmm_lang_exceptions'"},
	    'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
	    'lang': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "'language'"}),
	    'lmm': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lang_exceptions'", 'db_column': "'location_mirror_map_id'", 'to': "orm['mirror.LocationMirrorMap']"})
	},
	'mirror.locationmirrormap': {
	    'Meta': {'object_name': 'LocationMirrorMap', 'db_table': "'mirror_location_mirror_map'"},
	    'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
	    'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'})
	},
	'mirror.productlanguage': {
	    'Meta': {'unique_together': "(('product', 'lang'),)", 'object_name': 'ProductLanguage', 'db_table': "'mirror_product_langs'"},
	    'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
	    'lang': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "'language'"}),
	    'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'to': "orm['mirror.Product']"})
	}
    }

    complete_apps = ['contenttypes', 'auth', 'mirror']
