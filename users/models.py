from django.contrib.auth.models import User as DjangoUser
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

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = 'mirror_users'
        managed = False
        verbose_name = 'Legacy User'


class UserProfile(models.Model):
    """
    Represents additional data associated with a user account.
    For example used for mirror admin contact info.
    """
    user = models.ForeignKey(DjangoUser, unique=True, on_delete=models.CASCADE)

    # mirror contact info (bug 408677)
    address = models.TextField(verbose_name='Mailing Address', blank=True)
    phone_number = models.CharField(
        max_length=32, verbose_name='Phone Number', blank=True)
    ircnick = models.CharField(
        max_length=32,
        verbose_name='IRC Nick',
        help_text='Nickname on irc.mozilla.org',
        blank=True)
    comments = models.TextField(blank=True)


def user_post_save(sender, instance, **kwargs):
    """Create a user profile whenever a new user is created"""
    profile, new = UserProfile.objects.get_or_create(user=instance)


# listen to post-save signal
models.signals.post_save.connect(user_post_save, DjangoUser)
