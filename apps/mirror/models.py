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
    def __unicode__(self):
        return self.mirror_name

    class Meta:
        db_table = 'mirror_mirrors'
        managed = False


class OS(models.Model):
    """represents a platform, e.g., osx"""
    os_id = models.AutoField(primary_key=True)
    os_name = models.CharField(max_length=32, unique=True)
    os_priority = models.IntegerField()

    def __unicode__(self):
        return self.os_name

    class Meta:
        db_table = 'mirror_os'
        managed = False
        verbose_name = 'OS'
        verbose_name_plural = 'OSes'


class Product(models.Model):
    """represents a single product, e.g., Firefox-3.5.6"""
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255, unique=True)
    product_priority = models.IntegerField()
    product_count = models.DecimalField(max_digits=20, decimal_places=0)
    product_active = models.BooleanField(db_index=True)
    product_checknow = models.BooleanField(db_index=True)

    def __unicode__(self):
        return self.product_name

    class Meta:
        db_table = 'mirror_products'
        managed = False


class Lang(models.Model):
    """represents a locale, e.g., en-US"""
    lang_id = models.AutoField(primary_key=True)
    lang = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.lang

    class Meta:
        db_table = 'mirror_langs'
        managed = False


# XXX: old 'mirror_sessions' table not represented as a model


class User(models.Model):
    """represents a user who can log into this app"""
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=32)
    user_firstname = models.CharField(max_length=255)
    user_lastname = models.CharField(max_length=255)
    user_email = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = 'mirror_users'
        managed = False


class Location(models.Model):
    """represents a single location (i.e., file) on a mirror"""
    location_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product')
    os = models.ForeignKey('OS')
    location_path = models.CharField(max_length=255)
    lang = models.ForeignKey('Lang', null=True)

    def __unicode__(self):
        return self.location_path

    class Meta:
        db_table = 'mirror_locations'
        managed = False
        unique_together = ('location_id', 'product', 'os', 'lang')


class LocationMirrorMap(models.Model):
    """MtM mapping between Locations and Mirrors"""
    location = models.ForeignKey('Location')
    mirror = models.ForeignKey('Mirror')
    location_active = models.BooleanField()

    def __unicode__(self):
        return "%s %s" % (self.location, self.mirror)

    class Meta:
        db_table = 'mirror_location_mirror_map'
        managed = False

