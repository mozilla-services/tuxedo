from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class LegacyUser(models.Model):
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
    email = models.CharField(
        max_length=255, unique=True, db_column='user_email')
    converted = models.BooleanField()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'mirror_users'
        managed = False
        verbose_name = 'Legacy User'


class User(AbstractUser):
    pass
