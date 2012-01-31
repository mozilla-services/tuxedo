from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.html import escape

from product_details import product_details


# get the possible languages from product details
LANG_CHOICES = [(key, "%s: %s" % (key, value['English']))
                for key, value in product_details.languages.items()]

class Mirror(models.Model):
    """A single mirror."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True, verbose_name='Host Name')
    baseurl = models.CharField(max_length=255, verbose_name='Base URL',
                               help_text='No trailing slash.')
    rating = models.IntegerField()
    active = models.BooleanField()
    count = models.DecimalField(max_digits=20, decimal_places=0, default=0,
                                 db_index=True)
    regions = models.ManyToManyField('geoip.Region',
                                     db_table='geoip_mirror_region_map')
    contacts = models.ManyToManyField(User, verbose_name="Admin Contact",
                                      blank=True, null=True)

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
    """A platform, e.g., osx."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    priority = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_os'
        verbose_name = 'Operating System'


class Product(models.Model):
    """A single product, e.g., Firefox-3.5.6."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True,
                            verbose_name='Product Name')
    priority = models.IntegerField(default=1)
    count = models.DecimalField(max_digits=20, decimal_places=0, default=0,
                                verbose_name='Downloads')
    active = models.BooleanField(db_index=True, default=True)
    checknow = models.BooleanField(db_index=True, verbose_name='Check Now?',
                                   default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mirror_products'


class ProductLanguage(models.Model):
    """
    The languages a product is available in. No entries in this table means
    "all languages" or "not applicable".
    """
    product = models.ForeignKey('Product', related_name='languages')
    lang = models.CharField(max_length=30, choices=LANG_CHOICES,
                            db_column='language', verbose_name='Language')

    class Meta:
        db_table = 'mirror_product_langs'
        unique_together = ('product', 'lang')

    def __unicode__(self):
        return u"%s (%s)" % (self.product, self.lang)


class Location(models.Model):
    """A single location (i.e., file) on a mirror."""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product')
    os = models.ForeignKey('OS', verbose_name='OS')
    path = models.CharField(
        max_length=255, help_text=(
            "Always use a leading slash.<br/>"
            'The placeholder :lang will be replaced with the requested '
            'language at download time.'))

    class Meta:
        db_table = 'mirror_locations'
        unique_together = ('product', 'os')

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
        try:
            return u"%s - %s" % (self.location, self.mirror)
        except (Location.DoesNotExist, Mirror.DoesNotExist):
            return u"%s - %s" % (self.location_id, self.mirror_id)

    class Meta:
        db_table = 'mirror_location_mirror_map'


class LocationMirrorLanguageException(models.Model):
    """
    Exception from the rule that every available language is served by a
    mirror.

    We assume that mirrors that are listed in LocationMirrorMap as active
    serve the respective location in all available languages. Entries in
    this table mark the exceptions from that rule.
    """
    lmm = models.ForeignKey('LocationMirrorMap',
                            related_name='lang_exceptions',
                            db_column='location_mirror_map_id')
    lang = models.CharField(max_length=30, choices=LANG_CHOICES,
                            db_column='language', verbose_name='Language')

    class Meta:
        db_table = 'mirror_lmm_lang_exceptions'
        unique_together = ('lmm', 'lang')

    def __unicode__(self):
        return u"%s (%s)" % (unicode(self.lmm), self.lang)
