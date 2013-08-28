from xml.dom import minidom

from django.core.urlresolvers import reverse

from mirror.models import Location, OS

from . import testcases


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

    def test_location_add_new(self):
        """Add a new location through the API"""
        myproduct = self.products[0]
        myos = OS.objects.get(name='win')
        mypath = '/abc/def/file.bin'

        # remove possible conflicts from fixture
        myproduct.location_set.all().delete()

        response = self.c.post(reverse('api.views.location_add'),
                               {'product': myproduct.name,
                                'os': myos.name,
                                'path': mypath, })
        xmldoc = minidom.parseString(response.content)
        prod = xmldoc.getElementsByTagName('product')
        loc = prod[0].getElementsByTagName('location')

        self.assertEqual(prod[0].getAttribute('name'), myproduct.name,
                         'chosen product returned')
        self.assertTrue(int(loc[0].getAttribute('id')) > 0,
                        'new location id returned')
        self.assertEqual(loc[0].getAttribute('os'), myos.name,
                         'chosen os returned')
        self.assertEqual(loc[0].childNodes[0].data, mypath,
                         'location path returned')

        try:
            new_location = Location.objects.get(product=myproduct,
                                                os=myos)
        except Location.DoesNotExist:
            new_location = None
        self.assert_(new_location, 'new location was added to DB')

    def test_location_delete(self):
        """Delete a location by ID"""
        myloc = Location.objects.all()[0]
        response = self.c.post(reverse('api.views.location_delete'),
                               {'location_id': myloc.pk})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('success')
        self.assertEqual(len(msg), 1, 'Delete successful')

        try:
            this_location = Location.objects.get(pk=myloc.pk)
        except Location.DoesNotExist:
            this_location = None
        self.assertFalse(this_location, 'location was deleted')

        response = self.c.post(reverse('api.views.location_delete'),
                               {'location_id': myloc.pk})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        self.assertEqual(len(msg), 1, 'Delete is only successful once')


class UptakeTest(testcases.UptakeTestCase):

    def test_fuzzy(self):
        """List product uptake on mirrors"""
        testprod = self.products[0]

        # without fuzzy product matching
        response = self.c.get(reverse('api.views.uptake'),
                              {'product': testprod.name[:-3]})
        xmldoc = minidom.parseString(response.content)
        items = xmldoc.getElementsByTagName('item')
        self.assertEquals(len(items), 0, 'no fuzzy matching unless requested')

        response = self.c.get(reverse('api.views.uptake'),
                              {'product': testprod.name})
        xmldoc = minidom.parseString(response.content)
        items = xmldoc.getElementsByTagName('item')
        self.assertTrue(len(items) > 0, 'exact product matching')

        # with fuzzy product matching
        response = self.c.get(reverse('api.views.uptake'),
                              {'product': testprod.name[:-3],
                               'fuzzy': True})
        xmldoc = minidom.parseString(response.content)
        items = xmldoc.getElementsByTagName('item')
        self.assertTrue(len(items) > 0, 'fuzzy product matching')
