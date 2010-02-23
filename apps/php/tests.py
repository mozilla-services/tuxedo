"""
tests for the bounce script (written in PHP)
set the php script up at a URL and define it in settings.py
"""
import httplib
from urlparse import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase


class BounceTest(TestCase):
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

