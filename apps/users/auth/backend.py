import hashlib

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db import transaction

from users.models import LegacyUser


class ConversionBackend(ModelBackend):
    """Converts old-style `mirror_users` users to django users"""

    @transaction.commit_on_success
    def authenticate(self, username=None, password=None):
        pwhash = hashlib.md5(password).hexdigest()
        try:
            olduser = LegacyUser.objects.get(username=username,
                                             password=pwhash,
                                             converted=False)
        except LegacyUser.DoesNotExist:
            return None

        # mark old user as converted
        olduser.converted = True
        olduser.save()

        # create new django user
        newuser = User.objects.create_superuser(username=username,
                                                password=password,
                                                email=olduser.email)
        # move over first and last name
        newuser.first_name = olduser.firstname
        newuser.last_name = olduser.lastname
        # make sure we don't come back here
        newuser.backend = 'django.contrib.auth.backends.ModelBackend'
        newuser.save()

        return newuser
