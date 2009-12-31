from django.db import models


class Mirror(models.Model):
    """represents a single mirror"""
    id = models.AutoField(primary_key=True, db_column='mirror_id')
    name = models.CharField(max_length=64, unique=True, db_column='mirror_name',
                            verbose_name='Host Name')
    baseurl = models.CharField(max_length=255, db_column='mirror_baseurl',
                               verbose_name='Address')
    rating = models.IntegerField(db_column='mirror_rating')
    active = models.BooleanField(db_column='mirror_active')
    count = models.DecimalField(max_digits=20, decimal_places=0,
                                db_column='mirror_count', db_index=True)
    regions = models.ManyToManyField('geoip.Region',
                                     db_table='mirror_mirror_region_map')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_mirrors'
        managed = False


class OS(models.Model):
    """represents a platform, e.g., osx"""
    id = models.AutoField(primary_key=True, db_column='os_id')
    name = models.CharField(max_length=32, unique=True, db_column='os_name')
    priority = models.IntegerField(db_column='os_priority')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_os'
        managed = False
        verbose_name = 'OS'
        verbose_name_plural = 'OSes'


class Product(models.Model):
    """represents a single product, e.g., Firefox-3.5.6"""
    id = models.AutoField(primary_key=True, db_column='product_id')
    name = models.CharField(max_length=255, unique=True,
                            db_column='product_name',
                            verbose_name='Product Name')
    priority = models.IntegerField(db_column='product_priority')
    count = models.DecimalField(max_digits=20, decimal_places=0,
                                db_column='product_count',
                                verbose_name='Downloads')
    active = models.BooleanField(db_index=True, db_column='product_active')
    checknow = models.BooleanField(db_index=True, db_column='product_checknow',
                                   verbose_name='Check Now?')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_products'
        managed = False


class Lang(models.Model):
    """represents a locale, e.g., en-US"""
    id = models.AutoField(primary_key=True, db_column='lang_id')
    lang = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.lang

    class Meta:
        db_table = 'mirror_langs'
        managed = False


# XXX: old 'mirror_sessions' table not represented as a model


class User(models.Model):
    """represents a user who can log into this app"""
    id = models.AutoField(primary_key=True, db_column='user_id')
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=32)
    firstname = models.CharField(max_length=255, db_column='user_firstname')
    lastname = models.CharField(max_length=255, db_column='user_lastname')
    email = models.CharField(max_length=255, unique=True,
                             db_column='user_email')
    converted = models.BooleanField()

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = 'mirror_users'
        managed = False
        verbose_name = 'Legacy User'
        verbose_name_plural = 'Legacy Users'


class Location(models.Model):
    """represents a single location (i.e., file) on a mirror"""
    id = models.AutoField(primary_key=True, db_column='location_id')
    product = models.ForeignKey('Product')
    os = models.ForeignKey('OS', verbose_name='OS')
    path = models.CharField(max_length=255, db_column='location_path')
    lang = models.ForeignKey('Lang', null=True, verbose_name='Locale')

    def __unicode__(self):
        return self.path

    class Meta:
        db_table = 'mirror_locations'
        managed = False
        unique_together = ('product', 'os', 'lang')


class LocationMirrorMap(models.Model):
    """MtM mapping between Locations and Mirrors"""
    location = models.ForeignKey('Location')
    mirror = models.ForeignKey('Mirror')
    active = models.BooleanField(db_column='location_active')

    def __unicode__(self):
        return "%s %s" % (self.location, self.mirror)

    class Meta:
        db_table = 'mirror_location_mirror_map'
        managed = False

