# Django settings for tuxedo project.
import logging
import os

# Make filepaths relative to settings.
ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

DEBUG = False
TEMPLATE_DEBUG = DEBUG
LOG_LEVEL = logging.DEBUG
logging.basicConfig()

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bouncer.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=InnoDB',
            'charset': 'utf8',
            'use_unicode': True,
        },
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
    # 'slave': {
    #     ...
    # },
}

# Cache Backend. Set up memcache here. Examples:
#CACHE_BACKEND = 'memcached://172.19.26.240:11211;172.19.26.242:11211/'
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '### change me ###'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

# auth backends: uses django first, and converts old Bouncer users as needed
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'users.auth.backend.ConversionBackend')

# user profile stuff
LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'tuxedo.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path('templates'))

# path to mozilla product details
PROD_DETAILS_DIR = path('inc', 'product-details', 'json')

INSTALLED_APPS = (
    'api',
    'mirror',
    'geoip',
    'lib',
    #'php', # enable this if you want to run tests on the bounce script
    'users',
    'product_details',
    'south',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'django.contrib.sessions',
    #'django.contrib.sites',
)

# the location_check management command can check for stale locations on a
# reference mirror and let you disable the ones that are not present there.
# Define your reference base url here.
REFERENCE_BASEURL = 'http://ftp.mozilla.org/pub/mozilla.org'

# the php app black box tests the bounce script. Set it up at a URL somewhere,
# point it to the same DB, and enter the URL here.
BOUNCER_PHP_URL = ''

# override this with local settings
try:
    from local_settings import *
except ImportError, exp:
    pass
