import hashlib

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from mirror.models import User as MirrorUser

class ConversionBackend(ModelBackend):
    """Converts old-style `mirror_users` users to django users"""

    def authenticate(self, username=None, password=None):
        pwhash = hashlib.md5(password).hexdigest()
        olduser = MirrorUser.objects.get(username=username, password=pwhash,
                                         converted=False)
        if not olduser:
            return None
        
        # mark old user as converted
        olduser.converted = True
        olduser.save()

        # create new django user
        newuser = User.objects.create_superuser(username=username, 
                                                password=password,
                                                email=olduser.email)
        # make sure we don't come back here
        newuser.backend = 'django.contrib.auth.backends.ModelBackend'
        newuser.save()

        return newuser

