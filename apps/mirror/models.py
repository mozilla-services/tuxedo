from django.db import models

from lib.product_details import locale_details


# get the possible languages from product details
LANG_CHOICES = locale_details().get_model_choices()

class Mirror(models.Model):
    """represents a single mirror"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True, verbose_name='Host Name')
    baseurl = models.CharField(max_length=255, verbose_name='Base URL')
    rating = models.IntegerField()
    active = models.BooleanField()
    count = models.DecimalField(max_digits=20, decimal_places=0, default=0,
                                 db_index=True)
    regions = models.ManyToManyField('geoip.Region',
                                     db_table='geoip_mirror_region_map')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_mirrors'


class OS(models.Model):
    """represents a platform, e.g., osx"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    priority = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_os'
        verbose_name = 'Operating System'


class Product(models.Model):
    """represents a single product, e.g., Firefox-3.5.6"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True,
                            verbose_name='Product Name')
    priority = models.IntegerField()
    count = models.DecimalField(max_digits=20, decimal_places=0,
                                verbose_name='Downloads')
    active = models.BooleanField(db_index=True)
    checknow = models.BooleanField(db_index=True, verbose_name='Check Now?')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_products'


class User(models.Model):
    """
    represents a legacy user who can log into this app
    Note: This model is unmanaged because it's not needed unless we're
    migrating from an older version of Bouncer.
    """
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


class Location(models.Model):
    """represents a single location (i.e., file) on a mirror"""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product')
    os = models.ForeignKey('OS', verbose_name='OS')
    path = models.CharField(max_length=255)
    lang = models.CharField(max_length=10, unique=True,
                            choices=LANG_CHOICES, verbose_name='Language')

    def __unicode__(self):
        return self.path

    class Meta:
        db_table = 'mirror_locations'
        unique_together = ('product', 'os', 'lang')


class LocationMirrorMap(models.Model):
    """MtM mapping between Locations and Mirrors"""
    location = models.ForeignKey('Location')
    mirror = models.ForeignKey('Mirror')
    active = models.BooleanField()

    def __unicode__(self):
        return "%s %s" % (self.location, self.mirror)

    class Meta:
        db_table = 'mirror_location_mirror_map'

