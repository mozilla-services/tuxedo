from xml.dom import minidom

from django.core.urlresolvers import reverse

from mirror.models import Location

import testcases


class LocationTest(testcases.LocationTestCase):

    def test_location_show(self):
        """Make sure all locations for a single product show up"""
        testprod = self.products[0]

        response = self.c.get(reverse('api.views.location_show'),
                              {'product': testprod.name})
        xmldoc = minidom.parseString(response.content)
        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), 1, 'returned exactly one product')

        locations = prods[0].getElementsByTagName('location')
        self.assertEqual(len(locations), len(self.locations[testprod.name]),
                         'return all locations for this product')

    def test_location_show_fuzzy(self):
        """Make sure locations for a partial product list work"""
        fuzzystring = 'odd'

        response = self.c.get(reverse('api.views.location_show'),
                              {'product': fuzzystring, 'fuzzy': True})
        xmldoc = minidom.parseString(response.content)
        prods = xmldoc.getElementsByTagName('product')

        for prod in prods:
            prodname = prod.getAttribute('name')
            locations = prod.getElementsByTagName('location')
            self.assertEqual(len(locations), len(self.locations[prodname]),
                             'return all locations for this product')

