import ipaddr

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.utils.html import escape


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
        db_table = 'geoip_country_to_region'
        verbose_name_plural = 'Countries'


class IPBlock(models.Model):
    """returns a GeoIP mapping from an IP block to a country"""
    ip_start = models.DecimalField(max_digits=12, decimal_places=0)
    ip_end = models.DecimalField(max_digits=12, decimal_places=0)
    country = models.ForeignKey('Country', db_column='country_code')

    @property
    def ip_start_addr(self):
        return ipaddr.IPAddress(self.ip_start).compressed

    @ip_start_addr.setter
    def ip_start_addr(self, value):
        self.ip_start = int(ipaddr.IPAddress(value))

    @property
    def ip_end_addr(self):
        return ipaddr.IPAddress(self.ip_end).compressed

    @ip_end_addr.setter
    def ip_end_addr(self, value):
        self.ip_end = int(ipaddr.IPAddress(value))

    def __unicode__(self):
        return u"%s -- %s" % (self.ip_start_addr, self.ip_end_addr)

    class Meta:
        db_table = 'geoip_ip_to_country'
        verbose_name = 'IP Block'


class Region(models.Model):
    """represents a geographical region, e.g., Europe"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Region Name')
    priority = models.IntegerField(help_text='The lower the number, the '
                                             'higher the priority')
    throttle = models.IntegerField(verbose_name='GeoIP Throttle')
    fallback = models.ForeignKey('Region', null=True, blank=True)
    prevent_global_fallback = models.BooleanField(default=False)

    class Meta:
        db_table = 'geoip_regions'

    def __unicode__(self):
        return self.name

    def members(self):
        """HTML list of mirrors contained in this region."""
        mirrors = self.mirror_set.order_by('name')
        mirror_list = ['<a href="%s">%s</a>' % (
            reverse('admin:mirror_mirror_change', args=(m.pk,)),
            escape(m.name)) for m in mirrors]
        return '<br/>'.join(mirror_list) or ''
    members.allow_tags = True

    def mirror_count(self):
        return self.mirror_set.count()
    mirror_count.short_description = 'Mirrors'

    def ratings(self):
        return self.mirror_set.aggregate(Sum('rating'))['rating__sum']
    ratings.short_description = 'Total Ratings'
