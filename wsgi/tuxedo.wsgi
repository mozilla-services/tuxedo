import os
import site
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))

ALLDIRS = []

ALLDIRS.append(os.path.abspath('%s/../vendor/lib/python' % current_dir))
ALLDIRS.append(os.path.abspath('%s/../vendor/src' % current_dir))

for item in ALLDIRS:
    sys.path.append(item)

import django.core.handlers.wsgi

# Add the parent dir of tuxedo to the python path so we can import manage
# (which sets other path stuff) and settings.
wsgidir = os.path.dirname(__file__)
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../../')))

# manage adds the `apps` and `lib` directories to the path.
import tuxedo.manage

os.environ['DJANGO_SETTINGS_MODULE'] = 'tuxedo.settings'

# This is what mod_wsgi runs.
application = django.core.handlers.wsgi.WSGIHandler()
