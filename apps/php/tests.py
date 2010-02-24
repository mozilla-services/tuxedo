"""
tests for the bounce script (written in PHP)
set the php script up at a URL and define it in settings.py
NOTE: Unless the PHP script shares the data from the locations fixture,
      these tests will fail.
"""
import httplib
import urllib
from urlparse import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from mirror.models import Location, Product


class BounceTestCase(TestCase):
    fixtures = ['locations.json'] # Firefox 3.5 goodness

    def setUp(self):
        if not settings.BOUNCER_PHP_URL:
            raise ImproperlyConfigured()
        self.url = settings.BOUNCER_PHP_URL
        self.parsed_url = urlparse(self.url)
        self.conn = httplib.HTTPConnection(self.parsed_url.netloc)

    def test_noparams(self):
        """A request with no parameters should forward to mozilla.com"""
        self.conn.request('HEAD', self.parsed_url.path)
        req = self.conn.getresponse()
        self.assertEqual(req.status, 302)
        self.assertTrue(req.getheader('Location', '').startswith(
            'http://www.mozilla.com'))

    def test_defaults(self):
        """
        A product request with no lang or os defined should default to
        Windows and en-US
        """
        # get test product for these values
        myloc = Location.objects.filter(
            os__name='win', lang='en-US').order_by('?')[0]
        myprod = myloc.product

        data = {'product': myprod.name}

        self.conn.request('HEAD', '%s?%s' % (self.parsed_url.path,
                                             urllib.urlencode(data)))
        req = self.conn.getresponse()
        self.assertEqual(req.status, 302)
        self.assertTrue(req.getheader('Location', '').endswith(
            myloc.path))

    def test_languages_and_oses(self):
        """Test all known locations"""
        locs = Location.objects.all()

        for loc in locs:
            data = {'product': loc.product.name,
                    'os': loc.os.name,
                    'lang': loc.lang}

            self.conn.request('HEAD', '%s?%s' % (self.parsed_url.path,
                                                 urllib.urlencode(data)))
            req = self.conn.getresponse()
            self.assertEqual(req.status, 302)
            self.assertTrue(req.getheader('Location', '').endswith(
                loc.path))

