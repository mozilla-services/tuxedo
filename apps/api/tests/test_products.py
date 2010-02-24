from xml.dom import minidom

from django.core.urlresolvers import reverse

from mirror.models import Product

from . import testcases


class ProductTest(testcases.ProductTestCase):

    def test_product_show_all(self):
        """Make sure all products show up"""
        response = self.c.get(reverse('api.views.product_show'))
        xmldoc = minidom.parseString(response.content)
        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), len(self.products),
                         'need to return all products')

    def test_product_show_partial(self):
        """Make sure partial product list works"""
        response = self.c.get(reverse('api.views.product_show'),
                              {'product': 'odd', 'fuzzy': True})
        xmldoc = minidom.parseString(response.content)
        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), len(self.products)/2,
                         'need to return partial product list')

        response = self.c.get(reverse('api.views.product_show'),
                              {'product': 'odd'})
        xmldoc = minidom.parseString(response.content)
        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), 0, 'exact name matching of product names')

    def test_product_add_new(self):
        """Add a new product through the API"""
        new_prod = "Firefox"

        response = self.c.post(reverse('api.views.product_add'),
                               {'product': new_prod})
        xmldoc = minidom.parseString(response.content)

        all_products = Product.objects.all()
        self.assertEqual(len(all_products), len(self.products)+1,
                        'new product was added')

        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), 1, 'one product added and returned')
        self.assertTrue(int(prods[0].getAttribute('id')) > 0,
                        'new product id returned')
        self.assertEqual(prods[0].childNodes[0].data, new_prod,
                        'product name returned')

    def test_product_add_existing(self):
        """Adding an existing product will be handled gracefully"""
        new_prod = self.products[0].name

        response = self.c.post(reverse('api.views.product_add'),
                               {'product': new_prod})
        xmldoc = minidom.parseString(response.content)

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products),
                         'existing product not re-added')

        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), 1, 'one product returned')
        self.assertEqual(int(prods[0].getAttribute('id')), self.products[0].id,
                        'existing product id returned')
        self.assertEqual(prods[0].childNodes[0].data, new_prod,
                          'product name returned')

    def test_product_delete_byname(self):
        """Delete a product by name"""
        response = self.c.post(reverse('api.views.product_delete'),
                               {'product': self.products[0].name})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('success')
        self.assertEqual(len(msg), 1, 'Delete successful')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products)-1,
                         'product was deleted')

        response = self.c.post(reverse('api.views.product_delete'),
                               {'product': self.products[0].name})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        self.assertEqual(len(msg), 1, 'Delete is only successful once')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products)-1,
                         'product was deleted only once')

    def test_product_delete_byid(self):
        """Delete a product by ID"""
        response = self.c.post(reverse('api.views.product_delete'),
                               {'product_id': self.products[0].pk})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('success')
        self.assertEqual(len(msg), 1, 'Delete successful')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products)-1,
                         'product was deleted')

        response = self.c.post(reverse('api.views.product_delete'),
                               {'product_id': self.products[0].pk})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        self.assertEqual(len(msg), 1, 'Delete is only successful once')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products)-1,
                         'product was deleted only once')
