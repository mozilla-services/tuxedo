from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.html import escape

from lib.product_details import LocaleDetails


# get the possible languages from product details
LANG_CHOICES = LocaleDetails().get_model_choices()

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
    contacts = models.ManyToManyField(User, verbose_name="Admin Contact")

    class Meta:
        db_table = 'mirror_mirrors'

    def __unicode__(self):
        return self.name

    def admin_contacts(self):
        """get the administrative contacts for this mirror as HTML"""
        contacts = self.contacts.order_by('last_name', 'first_name')
        contacts = ['<a href="%s">%s</a>' % (
                        reverse('admin:auth_user_change', args=(c.pk,)),
                        escape('%s: %s' % (c.get_full_name() or c.username,
                                           c.email))
                    ) for c in contacts]
        return "<br/>".join(contacts) or ''
    admin_contacts.allow_tags = True


class OS(models.Model):
    """represents a platform, e.g., osx"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    priority = models.IntegerField(default=0)

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
    priority = models.IntegerField(default=1)
    count = models.DecimalField(max_digits=20, decimal_places=0, default=0,
                                verbose_name='Downloads')
    active = models.BooleanField(db_index=True, default=True)
    checknow = models.BooleanField(db_index=True, verbose_name='Check Now?',
                                   default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_products'


class Location(models.Model):
    """represents a single location (i.e., file) on a mirror"""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product')
    os = models.ForeignKey('OS', verbose_name='OS')
    path = models.CharField(max_length=255)
    lang = models.CharField(max_length=30, null=True, choices=LANG_CHOICES,
                            verbose_name='Language')

    class Meta:
        db_table = 'mirror_locations'
        unique_together = ('product', 'os', 'lang')

    def __unicode__(self):
        return self.path

    @staticmethod
    def get_mirror_uptake(products=None, oses=None,
                          order_by='location__product__name'):
        """
        Given a list of product IDs and/or OS IDs, return a list of these
        products' locations' mirror uptake
        """
        locations = LocationMirrorMap.objects \
            .filter(active=True, mirror__active=True)
        if products:
            locations = locations.filter(location__product__id__in=products)
        if oses:
            locations = locations.filter(location__os__id__in=oses)
        locations = locations \
            .values('location__id', 'location__product__name',
                    'location__os__name') \
            .annotate(available=models.Sum('mirror__rating')) \
            .order_by(order_by)
        locations = list(locations)

        # calculate totals
        total = Mirror.objects.filter(active=True) \
                .aggregate(total=models.Sum('rating'))['total']
        for location in locations:
            location.update({'total': total})
        return locations


class LocationMirrorMap(models.Model):
    """MtM mapping between Locations and Mirrors"""
    location = models.ForeignKey('Location')
    mirror = models.ForeignKey('Mirror')
    active = models.BooleanField()

    def __unicode__(self):
        return "%s %s" % (self.location, self.mirror)

    class Meta:
        db_table = 'mirror_location_mirror_map'

