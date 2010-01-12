from json import JSONDecoder
import os

import settings


class _json_details(object):
    """superclass for all JSON-based product and locale data"""
    json_file = os.path.join(settings.PRODUCT_DETAILS, 'json', '%s.json')
    json_data = {}

    def _get_json_data(self, filename):
        """grab and cache raw data from json file"""
        try:
            return self.json_data[filename]
        except KeyError:
            source = open(self.json_file % filename)
            self.json_data[filename] = JSONDecoder().decode(source.read())
            source.close()
            return self.json_data[filename]

class locale_details(_json_details):
    """language-specific data"""

    def get_languages(self):
        return self._get_json_data('languages')

