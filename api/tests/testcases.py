from django.contrib.auth.models import User
from django import test

from mirror.models import Location, LocationMirrorMap, Mirror, OS, Product


class APITestCase(test.TestCase):
    """The mother of all API tests"""
    def setUp(self):
        # user and login
        username = 'john'
        pw = 'johnpw'

        self.user = User.objects.create_user(
            username, 'lennon@thebeatles.com', pw
        )

        self.user.is_staff = True
        self.user.save()
        self.c = test.client.Client()
        self.c.login(username=username, password=pw)


class ProductTestCase(APITestCase):
    """TestCase publishing some default products"""

    def setUp(self):
        super(ProductTestCase, self).setUp()

        self.locales = ('ar', 'da', 'vi')

        # products
        self.products = []
        for i in range(1, 11):
            name = 'Product-%s-%s' % (i, i % 2 and 'odd' or 'even')
            p = Product(name=name)
            p.save()

            for lang in self.locales:
                p.languages.create(lang=lang)

            self.products.append(p)


class LocationTestCase(ProductTestCase):
    """TestCase publishing some default locations"""

    def setUp(self):
        super(LocationTestCase, self).setUp()

        # OSes
        for os in ['win', 'osx', 'linux']:
            OS.objects.create(name=os)

        # locations
        self.locations = {}
        for p in self.products:
            self.locations[p.name] = []
            for os in OS.objects.all():
                path = '/%s/location.%s.bin' % (p.name, os)

                loc = Location(product=p, os=os, path=path)
                loc.save()

                self.locations[p.name].append(loc)


class UptakeTestCase(LocationTestCase):
    """TestCase publishing some default mirrors"""

    def setUp(self):
        super(UptakeTestCase, self).setUp()

        # mirrors
        self.mirrors = []
        for i in range(1, 6):
            name = 'Mirror-%d' % i
            m = Mirror(name=name, rating=0, active=True)
            m.save()
            self.mirrors.append(m)

        # locationmirrormap
        for m in self.mirrors:
            for p, locs in self.locations.items():
                for l in locs:
                    # make half of them active
                    lmm = LocationMirrorMap(location=l, mirror=m,
                                            active=(l.id % 2))
                    lmm.save()
