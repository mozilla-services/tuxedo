import ipaddr

from django.db import models
from django.db.models import Sum


class Country(models.Model):
    """represents a country-to-region mapping for GeoIP"""
    country_code = models.CharField(help_text='ISO 3166 alpha2 country code',
                                    max_length=2,
                                    primary_key=True)
    region = models.ForeignKey('Region', null=True)
    country_name = models.CharField(max_length=255)
    continent = models.CharField(max_length=2)

    def __unicode__(self):
        return "%s (%s)" % (self.country_name, self.country_code)

    class Meta:
        db_table = 'mirror_country_to_region'
        managed = False
        verbose_name_plural = 'Countries'


class IPBlock(models.Model):
    """returns a GeoIP mapping from an IP block to a country"""
    # TODO dotted-quad representations
    ip_start = models.DecimalField(max_digits=12, decimal_places=0)
    ip_end = models.DecimalField(max_digits=12, decimal_places=0)
    country = models.ForeignKey('Country', db_column='country_code')

    @property
    def ip_start_addr(self):
        return ipaddr.IPAddress(self.ip_start).compressed

    @property
    def ip_end_addr(self):
        return ipaddr.IPAddress(self.ip_end).compressed

    def __unicode__(self):
       return u"%s -- %s" % (self.ip_start_addr, self.ip_end_addr)

    class Meta:
        db_table = 'mirror_ip_to_country'
        managed = False
        verbose_name = 'IP Block'


class Region(models.Model):
    """represents a geographical region, e.g., Europe"""
    id = models.AutoField(primary_key=True, db_column='region_id')
    name = models.CharField(max_length=255, db_column='region_name',
                            verbose_name='Region Name')
    priority = models.IntegerField(db_column='region_priority',
                                   help_text='The lower the number, the '
                                             'higher the priority')
    throttle = models.IntegerField(db_column='region_throttle',
                                   verbose_name='GeoIP Throttle')

    def mirror_count(self):
        return len(self.mirror_set.all())
    mirror_count.short_description = 'Mirrors'

    def ratings(self):
        return self.mirror_set.all().aggregate(Sum('rating'))['rating__sum']
    ratings.short_description = 'Total Ratings'

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_regions'
        managed = False

