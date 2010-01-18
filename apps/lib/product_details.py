from json import JSONDecoder
import os

from django.conf import settings


class _JSONDetails(object):
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

class LocaleDetails(_JSONDetails):
    """language-specific data"""

    def get_languages(self):
        return self._get_json_data('languages')

    def get_locale_codes(self):
        """return a list of all known locale codes"""
        langs = self.get_languages()
        locale_codes = langs.keys()
        locale_codes.sort()
        return locale_codes

    def get_model_choices(self):
        """
        Get list of languages usable as 'choices' for Django model fields.
        Will be sorted by their English name"""
        # TODO cache this if it is called repeatedly
        langs = self.get_languages()
        choices = [(key, "%s: %s" % (key, value['English']))
                   for key, value in langs.items()]
        choices.sort()
        return choices

