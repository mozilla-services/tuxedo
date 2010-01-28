import os
import xml.dom.minidom

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext

from mirror.models import Location, OS, Product

from .decorators import is_staff_or_basicauth, logged_in_or_basicauth


HTTP_AUTH_REALM = 'Bouncer API'

def _get_command_list():
    templates = os.listdir(os.path.join(os.path.dirname(__file__), 'templates',
                                        'api', 'docs'))
    # cut out the command names only
    commands = [ t[:-5] for t in templates if t.endswith('.html') ]
    commands.sort()
    return commands

def docindex(request):
    """API Doc Index"""
    data = {'commands': _get_command_list()}
    return render_to_response('api/index.html', data, context_instance=
                              RequestContext(request))

def docs(request, command):
    """Individual API docs"""
    if command not in _get_command_list():
        raise Http404
    data = {'command': command}
    return render_to_response('api/docs/%s.html' % command, data,
                              context_instance=RequestContext(request))

@is_staff_or_basicauth(HTTP_AUTH_REALM)
def uptake(request):
    """ping mirror uptake"""
    product = request.GET.get('product', None)
    os = request.GET.get('os', None)
    if not product and not os:
        return HttpResponseBadRequest('product and/or os are required GET '\
                                      'parameters.')

    if product:
        products = Product.objects.filter(name__icontains=product)
        pids = [ p.id for p in products ]
    else:
        pids = None

    if os:
        oses = OS.objects.filter(name__icontains=os)
        osids = [ o.id for o in oses ]
    else:
        osids = None

    uptake = Location.get_mirror_uptake(products=pids, oses=osids)

    xml = XMLRenderer()
    xml.prepare_uptake(uptake)
    return xml.render()


@logged_in_or_basicauth(HTTP_AUTH_REALM)
def product_show(request):
    product = request.GET.get('product', None)
    if product:
        products = Product.objects.filter(name__icontains=product) \
            .order_by('name')
    else:
        products = Product.objects.order_by('name')
    xml = XMLRenderer()
    xml.prepare_products(products)
    return xml.render()


@is_staff_or_basicauth(HTTP_AUTH_REALM)
def product_add(request):
    """
    Add a new product to the DB
    Will return the single product on success, or if it already existed.
    """
    xml = XMLRenderer()

    prodname = request.POST.get('product', None)
    if not prodname:
        return xml.error('Cannot add an empty product name')
    products = Product.objects.filter(name__exact=prodname)
    if not products:
        try:
            prod = Product(name=prodname)
            prod.save()
        except Exception, e:
            return xml.error(e)
        products = Product.objects.filter(pk=prod.pk)

    # success: return the single product to the user
    xml.prepare_products(products)
    return xml.render()


class XMLRenderer(object):
    """Render API data as XML"""

    def __init__(self):
        self.doc = xml.dom.minidom.Document()

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
            item.appendChild(self.doc.createTextNode(str(product.name)))
            item.setAttribute('id', str(product.id))
            root.appendChild(item)

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

    def error(self, message, render=True):
        """Prepare an error message"""
        root = self.doc.createElement('error')
        root.appendChild(self.doc.createTextNode(str(message)))
        self.doc.appendChild(root)
        if render:
            return self.render(status=400)

