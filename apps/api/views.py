import os
from xml.dom import minidom

from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from product_details import product_details

from api.decorators import has_perm_or_basicauth, logged_in_or_basicauth
from mirror.models import Location, Mirror, OS, Product, ProductAlias
from mirror.forms import ProductAliasForm

HTTP_AUTH_REALM = 'Bouncer API'


def _get_command_list():
    templates = os.listdir(os.path.join(os.path.dirname(__file__), 'templates',
                                        'api', 'docs'))
    # cut out the command names only
    commands = [t[:-5] for t in templates if t.endswith('.html')]
    commands.sort()
    return commands


def docindex(request):
    """API Doc Index"""
    data = {'commands': _get_command_list()}
    return render_to_response('api/index.html', data, context_instance=
                              RequestContext(request))


@require_GET
def docs(request, command):
    """Individual API docs"""
    if command not in _get_command_list():
        raise Http404
    data = {'command': command}

    # XXX special cases are ugly
    if command in ('product_add', 'product_language_add',
                   'product_language_delete'):
        langs = product_details.languages.keys()
        oses = OS.objects.order_by('name')
        os_list = [os.name for os in oses]
        data.update({'languages': langs,
                     'oses': os_list})

    return render_to_response('api/docs/%s.html' % command, data,
                              context_instance=RequestContext(request))


@has_perm_or_basicauth('mirror.view_uptake', HTTP_AUTH_REALM)
@require_GET
def uptake(request):
    """ping mirror uptake"""
    product = request.GET.get('product', None)
    os = request.GET.get('os', None)
    fuzzy = request.GET.get('fuzzy', False)
    xml = XMLRenderer()
    if not product and not os:
        return xml.error('product and/or os are required GET parameters.',
                         errno=101)

    if product:
        if fuzzy:
            products = Product.objects.filter(name__icontains=product)
        else:
            products = Product.objects.filter(name__exact=product)
        pids = [p.id for p in products]
        if not pids:
            return xml.error('No products found', errno=102)
    else:
        pids = None

    if os:
        if fuzzy:
            oses = OS.objects.filter(name__icontains=os)
        else:
            oses = OS.objects.filter(name__exact=os)
        osids = [o.id for o in oses]
        if not osids:
            return xml.error('No OSes found', errno=102)
    else:
        osids = None

    uptake = Location.get_mirror_uptake(products=pids, oses=osids)

    xml.prepare_uptake(uptake)
    return xml.render()


@require_GET
@logged_in_or_basicauth(HTTP_AUTH_REALM)
def mirror_list(request):
    mirrors = Mirror.objects.filter(active=True)
    xml = XMLRenderer()
    xml.prepare_mirrors(mirrors)
    return xml.render()


@require_GET
@logged_in_or_basicauth(HTTP_AUTH_REALM)
def product_show(request):
    product = request.GET.get('product', None)
    fuzzy = request.GET.get('fuzzy', False)
    if product:
        if fuzzy:
            products = Product.objects.filter(name__icontains=product)
        else:
            products = Product.objects.filter(name__exact=product)
    else:
        products = Product.objects
    products = products.order_by('name')
    xml = XMLRenderer()
    xml.prepare_products(products)
    return xml.render()


@require_POST
@csrf_exempt
@has_perm_or_basicauth('mirror.add_product', HTTP_AUTH_REALM)
def product_add(request):
    """
    Add a new product to the DB
    Will return the single product on success
    """
    xml = XMLRenderer()

    prodname = request.POST.get('product', None)
    if not prodname:
        return xml.error('Cannot add an empty product name', errno=103)

    # check languages
    langs = request.POST.getlist('languages')
    locales = product_details.languages.keys()
    if [l for l in langs if l not in locales]:
        return xml.error('invalid language code(s)', errno=103)

    # save new product
    products = Product.objects.filter(name__exact=prodname)
    if not products:
        try:
            prod = Product(name=prodname)
            prod.save()
            for lang in langs:
                prod.languages.create(lang=lang)
        except Exception, e:
            return xml.error(e)
        products = Product.objects.filter(pk=prod.pk)
    else:
        return xml.error('product already exists.', errno=104)

    # success: return the single product to the user
    xml.prepare_products(products)
    return xml.render()


@require_POST
@csrf_exempt
@has_perm_or_basicauth('mirror.delete_product', HTTP_AUTH_REALM)
def product_delete(request):
    """Remove a product from the DB"""
    xml = XMLRenderer()

    prod_id = request.POST.get('product_id', None)
    prodname = request.POST.get('product', None)
    if not (prod_id or prodname):
        return xml.error(
            'Either product_id or product is required.',
            errno=101
        )
    try:
        if prod_id:
            prod = Product.objects.get(pk=prod_id)
        else:
            prod = Product.objects.get(name=prodname)
    except Product.DoesNotExist:
        return xml.error('No product found.', errno=102)
    except Exception, e:
        return xml.error(e)

    try:
        prod.delete()
    except Exception, e:
        return xml.error(e)

    return xml.success('Deleted product: %s' % prod.name)


@require_POST
@csrf_exempt
@has_perm_or_basicauth('mirror.add_product_language', HTTP_AUTH_REALM)
def product_language_add(request):
    """
    Add a language to a product.
    Will return the single product on success
    """
    xml = XMLRenderer()

    prodname = request.POST.get('product', None)
    if not prodname:
        return xml.error('Product name is required.', errno=101)

    # find product
    products = Product.objects.filter(name__exact=prodname)
    if not products:
        return xml.error('Product not found.', errno=102)
    prod = products[0]

    # check languages
    langs = request.POST.getlist('languages')
    locales = product_details.languages.keys()
    if [l for l in langs if l not in locales]:
        return xml.error('Invalid language code(s)', errno=103)
    if prod.languages.filter(lang__in=langs):
        return xml.error('Language(s) already exist(s)', errno=104)

    # add languages
    try:
        for lang in langs:
            prod.languages.create(lang=lang)
    except Exception, e:
        return xml.error(e)
    products = Product.objects.filter(pk=prod.pk)

    # success: return the single product to the user
    xml.prepare_products(products)
    return xml.render()


@require_POST
@csrf_exempt
@has_perm_or_basicauth("mirror.delete_product_language", HTTP_AUTH_REALM)
def product_language_delete(request):
    """Delete a language from a product."""
    xml = XMLRenderer()

    prodname = request.POST.get('product', None)
    if not prodname:
        return xml.error('Product name is required.', errno=101)

    # find product
    products = Product.objects.filter(name__exact=prodname)
    if not products:
        return xml.error('Product not found.', errno=102)
    prod = products[0]

    # check and remove languages
    langs = request.POST.getlist('languages')
    if not langs:
        return xml.error('At least one language is required.', errno=101)

    # wildcard: remove all languages
    if len(langs) == 1 and langs[0] == '*':
        prod.languages.all().delete()
        return xml.success('Deleted all languages from product %s' % prod.name)

    locales = product_details.languages.keys()
    if [l for l in langs if l not in locales]:
        return xml.error('Invalid language code(s)', errno=103)

    try:
        prod.languages.filter(lang__in=langs).delete()
    except Exception, e:
        return xml.error(e)
    products = Product.objects.filter(pk=prod.pk)

    return xml.success('Deleted languages %s from product %s' % (
        ', '.join(langs), prod.name))


@require_GET
@logged_in_or_basicauth(HTTP_AUTH_REALM)
def location_show(request):
    xml = XMLRenderer()

    prodname = request.GET.get('product', None)
    fuzzy = request.GET.get('fuzzy', False)
    if not prodname:
        return xml.error('The GET parameter product is required', errno=103)

    if fuzzy:
        products = Product.objects.filter(name__icontains=prodname)
    else:
        products = Product.objects.filter(name__exact=prodname)
    products = products.order_by('name')

    for product in products:
        locations = Location.objects.filter(product__exact=product)
        xml.prepare_locations(product, locations)

    return xml.render()


@require_POST
@csrf_exempt
@has_perm_or_basicauth("mirror.add_location", HTTP_AUTH_REALM)
def location_add(request):
    """
    Add a new location to the DB
    Will return the single product on success
    """
    xml = XMLRenderer()

    prodname = request.POST.get('product', None)
    osname = request.POST.get('os', None)
    path = request.POST.get('path', None)
    if not (prodname and osname and path):
        return xml.error('product, os, and path are required POST parameters.',
                         errno=101)

    try:
        product = Product.objects.get(name=prodname)
        os = OS.objects.get(name=osname)
    except (Product.DoesNotExist, OS.DoesNotExist), e:
        return xml.error(e)

    # do not make duplicates
    dupes = Location.objects.filter(product=product, os=os).count()
    if dupes:
        return xml.error('The specified location already exists.', errno=104)

    try:
        location = Location(product=product, os=os, path=path)
        location.save(force_insert=True)
    except Exception, e:
        return xml.error(e)
    locations = Location.objects.filter(pk=location.pk)

    # success: return the single new location to the user
    xml.prepare_locations(product, locations)
    return xml.render()


@require_POST
@csrf_exempt
@has_perm_or_basicauth("mirror.delete_location", HTTP_AUTH_REALM)
def location_delete(request):
    """Remove a location from the DB"""
    xml = XMLRenderer()

    loc_id = request.POST.get('location_id', None)
    if not loc_id:
        return xml.error('location_id is required.', errno=101)
    try:
        location = Location.objects.get(pk=loc_id)
    except Location.DoesNotExist:
        return xml.error('No location found.', errno=102)
    except Exception, e:
        return xml.error(e)

    try:
        location.delete()
    except Exception, e:
        return xml.error(e)

    return xml.success('Deleted location: %s' % location)


@require_POST
@csrf_exempt
@has_perm_or_basicauth("mirror.create_update_alias", HTTP_AUTH_REALM)
def create_update_alias(request):
    """Create or update an alias for a product"""

    xml = XMLRenderer()

    form = ProductAliasForm(request.POST)
    if not form.is_valid():
        if 'alias' in form.errors:
            if 'required' in form.errors['alias'][0]:
                return xml.error(
                    'alias name is required.',
                    errno=form.E_ALIAS_REQUIRED
                )

            if 'same name' in form.errors['alias'][0]:
                return xml.error(
                    ('You cannot create an alias with the same name as a '
                     'product'),
                    errno=form.E_ALIAS_PRODUCT_MATCH
                )
        if 'related_product' in form.errors:
            if 'required' in form.errors['related_product'][0]:
                return xml.error(
                    'related_product name is required.',
                    errno=form.E_RELATED_NAME_REQUIRED
                )
            if 'same name as an existing' in form.errors['related_product'][0]:
                return xml.error(
                    'You cannot create alias with the same name as a product',
                    errno=form.E_ALIAS_PRODUCT_MATCH
                )
            if 'invalid' in form.errors['related_product'][0]:
                return xml.error(
                    'You must specify a valid product to match with an alias',
                    errno=form.E_PRODUCT_DOESNT_EXIST
                )

        return xml.error(
            'There was a problem validating the data provided',
            errno=form.E_ALIAS_GENERAL_VALIDATION_ERROR
        )

    alias = form.cleaned_data['alias']
    redirect = form.cleaned_data['related_product']

    alias_obj, created = ProductAlias.objects.get_or_create(
        alias=alias,
        defaults={'related_product': redirect}
    )

    if not created:
        alias_obj.related_product = redirect
        alias_obj.save()

    return xml.success('Created/updated alias %s' % alias)


class XMLRenderer(object):
    """Render API data as XML"""

    def __init__(self):
        self.doc = minidom.Document()

    def toxml(self):
        return self.doc.toxml(encoding='utf-8')

    def render(self, status=200):
        """serve the XML to the user"""
        return HttpResponse(self.toxml(), mimetype='text/xml', status=status)

    def prepare_products(self, products):
        """Product List"""
        root = self.doc.createElement('products')
        self.doc.appendChild(root)
        for product in products:
            item = self.doc.createElement('product')
            item.setAttribute('id', str(product.id))
            item.setAttribute('name', str(product.name))
            for lang in product.languages.all():
                lang_item = self.doc.createElement('language')
                lang_item.setAttribute('locale', str(lang.lang))
                item.appendChild(lang_item)
            root.appendChild(item)

    def prepare_mirrors(self, mirrors):
        """Mirror List"""
        root = self.doc.createElement('mirrors')
        self.doc.appendChild(root)
        for mirror in mirrors:
            item = self.doc.createElement('mirror')
            item.setAttribute('baseurl', str(mirror.baseurl))
            root.appendChild(item)

    def prepare_locations(self, product, locations):
        """Prepare list of locations for a given product"""
        root = self.doc.documentElement
        if not root:
            root = self.doc.createElement('locations')
            self.doc.appendChild(root)
        prodnode = self.doc.createElement('product')
        prodnode.setAttribute('id', str(product.pk))
        prodnode.setAttribute('name', product.name)
        root.appendChild(prodnode)

        for location in locations:
            locnode = self.doc.createElement('location')
            locnode.setAttribute('id', str(location.pk))
            locnode.setAttribute('os', str(location.os.name))
            locnode.appendChild(self.doc.createTextNode(location.path))
            prodnode.appendChild(locnode)

    def prepare_uptake(self, uptake):
        """Product uptake"""
        content_map = {'product': 'location__product__name',
                       'os': 'location__os__name',
                       'available': 'available',
                       'total': 'total'}

        root = self.doc.createElement('mirror_uptake')
        self.doc.appendChild(root)
        for row in uptake:
            item = self.doc.createElement('item')
            for key, value in content_map.iteritems():
                elem = self.doc.createElement(key)
                elem.appendChild(self.doc.createTextNode(str(row[value])))
                item.appendChild(elem)
            root.appendChild(item)

    def success(self, message, render=True):
        """Prepare a success message"""
        return self.message(message, type='success', render=render)

    def error(self, message, errno=0, render=True):
        """Prepare an error message"""
        return self.message(message, type='error', number=errno,
                            render=render, status=400)

    def message(self, message, type='info', number=None, render=True,
                status=200):
        """Prepare a single message"""
        root = self.doc.createElement(type)
        root.appendChild(self.doc.createTextNode(str(message)))
        if number:
            root.setAttribute('number', str(number))
        self.doc.appendChild(root)
        if render:
            return self.render(status)
