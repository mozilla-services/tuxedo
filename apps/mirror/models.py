from django.db import models

# todo:
# mirror_country_to_region
# mirror_ip_to_country
# mirror_langs
# mirror_locations
# mirror_location_mirror_map
# mirror_log
# mirror_mirror_region_map
# mirror_os
# mirror_products
# mirror_regions
# mirror_sessions
# mirror_users

class Mirrors(models.Model):
    mirror_id = models.AutoField(primary_key=True)
    mirror_name = models.CharField(max_length=32)
    mirror_baseurl = models.CharField(max_length=255)
    mirror_rating = models.IntegerField()
    mirror_active = models.BooleanField()
    mirror_count = models.DecimalField(max_digits=20, decimal_places=0)

