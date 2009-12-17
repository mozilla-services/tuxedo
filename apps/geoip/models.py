import ipaddr

from django.db import models


class Region(models.Model):
    """represents a geographical region, e.g., Europe"""
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=255)
    region_priority = models.IntegerField()
    region_throttle = models.IntegerField()

    def __unicode__(self):
        return self.region_name

    class Meta:
        db_table = 'mirror_regions'
        managed = False


class CountryToRegion(models.Model):
    """represents a country-to-region mapping for GeoIP"""
    country_code = models.CharField(help_text='ISO 3166 alpha2 country code',
                                    max_length=2,
                                    primary_key=True)
    region = models.ForeignKey('Region')
    country_name = models.CharField(max_length=255)
    continent = models.CharField(max_length=2)

    def __unicode__(self):
        return "%s (%s): %s" % (country_name, country_code, region)

    class Meta:
        db_table = 'mirror_country_to_region'
        managed = False


class IPToCountry(models.Model):
    """returns a GeoIP mapping from an IP block to a country"""
    # TODO dotted-quad representations
    ip_start = models.DecimalField(max_digits=12, decimal_places=0)
    ip_end = models.DecimalField(max_digits=12, decimal_places=0)
    country = models.ForeignKey('CountryToRegion', db_column='country_code')

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


class MirrorRegionMap(models.Model):
    """MtM mapping between Mirrors and Regions"""
    mirror = models.ForeignKey('mirror.Mirror')
    region = models.ForeignKey('Region')

    def __unicode(self):
        return "%s %s" % (self.mirror, self.region)

    class Meta:
        db_table = 'mirror_mirror_region_map'
        managed = False

