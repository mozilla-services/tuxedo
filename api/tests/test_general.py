from django.core.urlresolvers import resolve

from api import views

from . import testcases


class GeneralAPITest(testcases.APITestCase):

    def test_trailing_slashes_in_url(self):
        """Make sure all API calls work with and without trailing slash"""
        api_prefix = '/api/'
        for command in views._get_command_list():
            # will throw exception if unresolvable
            resolve(api_prefix + command)
            resolve('%s%s/' % (api_prefix, command))
