from xml.dom import minidom
from xml.etree import ElementTree

from django.core.urlresolvers import reverse

from mirror.models import Product
from mirror.forms import ProductAliasForm

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
        self.assertEqual(len(prods), len(self.products) / 2,
                         'need to return partial product list')

        response = self.c.get(reverse('api.views.product_show'),
                              {'product': 'odd'})
        xmldoc = minidom.parseString(response.content)
        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), 0, 'exact name matching of product names')

    def test_product_add_new(self):
        """Add a new product through the API"""
        new_prod = "Firefox"
        langs = ('en-US', 'fr', 'de')

        response = self.c.post(reverse('api.views.product_add'),
                               {'product': new_prod, 'languages': langs})
        xmldoc = minidom.parseString(response.content)

        all_products = Product.objects.all()
        self.assertEqual(len(all_products), len(self.products) + 1,
                         'new product was added')

        prods = xmldoc.getElementsByTagName('product')
        self.assertEqual(len(prods), 1, 'one product added and returned')
        self.assertTrue(int(prods[0].getAttribute('id')) > 0,
                        'new product id returned')
        self.assertEqual(prods[0].getAttribute('name'),
                         new_prod, 'product name returned')
        self.assertEqual(len(prods[0].childNodes), len(langs),
                         'all languages returned')

    def test_product_add_checknow(self):
        """Newly added products must have checknow flag set (bug 566852)"""
        new_prod = 'Firefox-10.0'
        self.c.post(reverse('api.views.product_add'),
                    {'product': new_prod})
        prod = Product.objects.get(name=new_prod)

        self.assertTrue(prod.checknow, 'checknow must be enabled.')

    def test_product_add_existing(self):
        """Adding an existing product should throw an error"""
        new_prod = self.products[0].name

        response = self.c.post(reverse('api.views.product_add'),
                               {'product': new_prod})
        xmldoc = minidom.parseString(response.content)

        err = xmldoc.getElementsByTagName('error')
        self.assertEqual(len(err), 1)
        self.assertEqual(int(err[0].getAttribute('number')), 104)

    def test_product_delete_byname(self):
        """Delete a product by name"""
        response = self.c.post(reverse('api.views.product_delete'),
                               {'product': self.products[0].name})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('success')
        self.assertEqual(len(msg), 1, 'Delete successful')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products) - 1,
                          'product was deleted')

        response = self.c.post(reverse('api.views.product_delete'),
                               {'product': self.products[0].name})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        errno = msg[0].getAttribute('number')
        self.assertEqual(len(msg), 1, 'Delete must only be successful once')
        self.assertEqual(int(errno), 102,
                         'must return product not found error')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products) - 1,
                          'product was deleted only once')

    def test_product_delete_byid(self):
        """Delete a product by ID"""
        response = self.c.post(reverse('api.views.product_delete'),
                               {'product_id': self.products[0].pk})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('success')
        self.assertEqual(len(msg), 1, 'Delete successful')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products) - 1,
                          'product was deleted')

        response = self.c.post(reverse('api.views.product_delete'),
                               {'product_id': self.products[0].pk})
        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        errno = msg[0].getAttribute('number')
        self.assertEqual(len(msg), 1, 'Delete must only be successful once')
        self.assertEqual(int(errno), 102,
                         'must return product not found error')

        all_products = Product.objects.all()
        self.assertEquals(len(all_products), len(self.products) - 1,
                          'product was deleted only once')

    def test_product_language_add(self):
        """Add some languages to an existing product."""
        mylangs = ('en-US', 'de', 'fr')
        response = self.c.post(reverse('api.views.product_language_add'),
                               {'product': self.products[0].name,
                                'languages': mylangs})
        xmldoc = ElementTree.XML(response.content)
        langs = xmldoc.findall('product/language')
        self.assertEqual(len(langs), len(mylangs) + len(self.locales))
        for lang in [l.get('locale') for l in langs]:
            assert lang in mylangs or lang in self.locales

    def test_product_language_delete(self):
        """Delete some languages from an existing product."""
        myprod = self.products[0]
        remove_langs = [l.lang for l in myprod.languages.all()[:2]]

        response = self.c.post(reverse('api.views.product_language_delete'),
                               {'product': self.products[0].name,
                                'languages': remove_langs})
        xmldoc = ElementTree.XML(response.content)
        self.assertEqual(xmldoc.tag, 'success')

        for lang in remove_langs:
            assert not myprod.languages.filter(lang=lang)

    def test_product_language_delete_all(self):
        """Delete all languages from a product via wildcard."""
        myprod = self.products[0]
        assert myprod.languages.count(), 'Test product needs languages.'

        response = self.c.post(reverse('api.views.product_language_delete'),
                               {'product': self.products[0].name,
                                'languages': '*'})
        xmldoc = ElementTree.XML(response.content)
        self.assertEqual(xmldoc.tag, 'success')

        assert not myprod.languages.count(), (
            'Wildcard must delete all languages.')

    def test_create_update_alias(self):

        Product.objects.create(name='MyTestProduct')
        Product.objects.create(name='MyTestProduct2')
        
        response = self.c.post(reverse('api.views.create_update_alias'),
                               {'alias': 'my-test-alias',
                                'related_product': 'MyTestProduct'})

        self.assertEqual(response.status_code, 200,
                         'Status code should be 200 when alias created')
        
        response = self.c.post(reverse('api.views.create_update_alias'),
                               {'alias': 'my-test-alias',
                                'related_product': 'MyTestProduct2'})
        
        self.assertEqual(response.status_code, 200,
                         'Updating a product should produce a 200 status code')

    def test_create_update_alias_requires_alias_name(self):
        Product.objects.create(name='MyTestProduct')

        response = self.c.post(reverse('api.views.create_update_alias'),
                               {'alias': '',
                                'related_product': 'MyTestProduct'})

        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        errno = msg[0].getAttribute('number')
        self.assertEqual(int(errno), ProductAliasForm.E_ALIAS_REQUIRED,
                         'alias is a required field')

    def test_create_update_alias_requires_valid_product_name(self):
        response = self.c.post(reverse('api.views.create_update_alias'),
                               {'alias': 'my-test-alias',
                                'related_product': ''})

        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        errno = msg[0].getAttribute('number')

        self.assertEqual(int(errno), ProductAliasForm.E_RELATED_NAME_REQUIRED,
                         'related_product is a required field')

        response = self.c.post(reverse('api.views.create_update_alias'),
                               {'alias': 'my-test-alias',
                                'related_product': 'MyTestProduct'})

        xmldoc = minidom.parseString(response.content)

        msg = xmldoc.getElementsByTagName('error')
        errno = msg[0].getAttribute('number')

        self.assertEqual(int(errno), ProductAliasForm.E_PRODUCT_DOESNT_EXIST,
                         'Must provide a valid product name')

        Product.objects.create(name='MyTestProduct')

        response = self.c.post(reverse('api.views.create_update_alias'),
                               {'alias': 'MyTestProduct',
                                'related_product': 'MyTestProduct'})

        xmldoc = minidom.parseString(response.content)
        msg = xmldoc.getElementsByTagName('error')
        errno = msg[0].getAttribute('number')
        self.assertEqual(int(errno), ProductAliasForm.E_ALIAS_PRODUCT_MATCH,
                         'Cannot specify the same alias as a product name')
