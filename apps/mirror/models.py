import ipaddr

from django.db import models


class Mirror(models.Model):
    """represents a single mirror"""
    mirror_id = models.AutoField(primary_key=True)
    mirror_name = models.CharField(max_length=64, unique=True)
    mirror_baseurl = models.CharField(max_length=255)
    mirror_rating = models.IntegerField()
    mirror_active = models.BooleanField()
    mirror_count = models.DecimalField(max_digits=20, decimal_places=0,
                                       db_index=True)

    class Meta:
        db_table = 'mirror_mirrors'
        managed = False


class OS(models.Model):
    """represents a platform, e.g., osx"""
    os_id = models.AutoField(primary_key=True)
    os_name = models.CharField(max_length=32, unique=True)
    os_priority = models.IntegerField()

    class Meta:
        db_table = 'mirror_os'
        managed = False


class Product(models.Model):
    """represents a single product, e.g., Firefox-3.5.6"""
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255, unique=True)
    product_priority = models.IntegerField()
    product_count = models.DecimalField(max_digits=20, decimal_places=0)
    product_active = models.BooleanField(db_index=True)
    product_checknow = models.BooleanField(db_index=True)

    class Meta:
        db_table = 'mirror_products'
        managed = False


class Lang(models.Model):
    """represents a locale, e.g., en-US"""
    lang_id = models.AutoField(primary_key=True)
    lang = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'mirror_langs'
        managed = False


class Region(models.Model):
    """represents a geographical region, e.g., Europe"""
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=255)
    region_priority = models.IntegerField()
    region_throttle = models.IntegerField()

    class Meta:
        db_table = 'mirror_regions'
        managed = False


# TODO User and Session may need to go into an auth app
class Session(models.Model):
    """represents a login session"""
    session_id = models.CharField(max_length=32, unique=True)
    username = models.CharField(max_length=32)

    class Meta:
        db_table = 'mirror_sessions'
        managed = False


class User(models.Model):
    """represents a user who can log into this app"""
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=32)
    user_firstname = models.CharField(max_length=255)
    user_lastname = models.CharField(max_length=255)
    user_email = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'mirror_users'
        managed = False


class MirrorLocation(models.Model):
    """represents a single location (i.e., file) on a mirror"""
    location_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey('Product')
    os_id = models.ForeignKey('OS')
    location_path = models.CharField(max_length=255)
    lang_id = models.ForeignKey('Lang', null=True)

    class Meta:
        db_table = 'mirror_locations'
        managed = False
        unique_together = ('location_id', 'product_id', 'os_id', 'lang_id')


class CountryToRegion(models.Model):
    """represents a country-to-region mapping for GeoIP"""
    country_code = models.CharField(help_text='ISO 3166 alpha2 country code',
                                    max_length=2,
                                    primary_key=True)
    region_id = models.ForeignKey('Region')
    country_name = models.CharField(max_length=255)
    continent = models.CharField(max_length=2)

    class Meta:
        db_table = 'mirror_country_to_region'
        managed = False


class IPToCountry(models.Model):
    """returns a GeoIP mapping from an IP block to a country"""
    # TODO dotted-quad representations
    ip_start = models.Decimalfield(max_digits=12, decimal_places=0)
    ip_end = models.Decimalfield(max_digits=12, decimal_places=0)
    country_code = models.ForeignKey('CountryToRegion')

    @property
    def ip_start_addr(self):
        return ipaddr.IP(self.ip_start).ip_ext

    @property
    def ip_end_addr(self):
        return ipaddr.IP(self.ip_end).ip_ext

    def __unicode__(self):
       return u"%s -- %s" % (self.ip_start_addr, self.ip_end_addr)

    class Meta:
        db_table = 'mirror_ip_to_country'
        managed = False


class LocationMirrorMap(models.Model):
    """MtM mapping between Locations and Mirrors"""
    location_id = models.ForeignKey('Location')
    mirror_id = models.ForeignKey('Mirror')
    location_active = models.BooleanField()

    class Meta:
        db_table = 'mirror_location_mirror_map'
        managed = False


class MirrorRegionMap(models.Model):
    """MtM mapping between Mirrors and Regions"""
    mirror_id = models.ForeignKey('Mirror')
    region_id = models.ForeignKey('Region')

    class Meta:
        db_table = 'mirror_mirror_region_map'
        managed = False

