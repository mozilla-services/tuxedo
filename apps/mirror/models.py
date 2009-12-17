from django.db import models

# todo:
# mirror_country_to_region
# mirror_ip_to_country
# mirror_location_mirror_map
# mirror_mirror_region_map

# *** basic entities ***

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


class OS(models.Model):
    """represents a platform, e.g., osx"""
    os_id = models.AutoField(primary_key=True)
    os_name = models.CharField(max_length=32, unique=True)
    os_priority = models.IntegerField()

    class Meta:
        db_table = 'mirror_os'


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


class Lang(models.Model):
    """represents a locale, e.g., en-US"""
    lang_id = models.AutoField(primary_key=True)
    lang = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'mirror_langs'


class Region(models.Model):
    """represents a geographical region, e.g., Europe"""
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=255)
    region_priority = models.IntegerField()
    region_throttle = models.IntegerField()

    class Meta:
        db_table = 'mirror_regions'


# TODO User and Session may need to go into an auth app
class Session(models.Model):
    """represents a login session"""
    session_id = models.CharField(max_length=32, unique=True)
    username = models.CharField(max_length=32)

    class Meta:
        db_table = 'mirror_sessions'


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


# *** complex entities ***

class MirrorLocation(models.Model):
    location_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey('Product')
    os_id = models.ForeignKey('OS')
    location_path = models.CharField(max_length=255)
    lang_id = models.ForeignKey('Lang', null=True)

    class Meta:
        db_table = 'mirror_locations'
        unique_together = ('location_id', 'product_id', 'os_id', 'lang_id')


# *** ManyToMany relationship models ***

