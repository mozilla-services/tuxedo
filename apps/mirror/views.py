from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.template import RequestContext
import django_tables as tables

from lib.sort_headers import SortHeaders
from models import LocationMirrorMap, Mirror
from forms import UptakeForm


UPTAKE_LIST_HEADERS = (
    ('Product', 'location__product__name'),
    ('OS', 'location__os__name'),
    ('Available', 'available'),
    ('Total', None),
    ('Percentage', None)
)
LOCATION_STATS_LIST_HEADERS = (
    ('Status', 'active'),
    ('Host Name', 'mirror__name'),
    ('Address', 'mirror__baseurl'),
    ('Path', 'location__path')
)

def index(request):
    """Main login/index page"""
    return render_to_response('index.html', context_instance=
                              RequestContext(request))

@login_required
def uptake(request):
    """Product Uptake on Mirrors"""
    if request.GET.get('p'):
        form = UptakeForm(request.GET)
    else:
        form = UptakeForm()

    data = {'form': form}

    if form.is_bound:
        sort_headers = SortHeaders(request, UPTAKE_LIST_HEADERS)
        products = [ int(p) for p in form.data.getlist('p') ]
        locations = LocationMirrorMap.objects \
            .filter(location__product__id__in=products, active=True,
                    mirror__active=True) \
            .values('location__id', 'location__product__name',
                    'location__os__name') \
            .annotate(available=Sum('mirror__rating')) \
            .order_by(sort_headers.get_order_by())
        locations = list(locations)

        # calculate totals and percentages
        total = Mirror.objects.filter(active=True) \
                .aggregate(total=Sum('rating'))['total']
        for location in locations:
            location.update({'total': total,
                             'percentage': 100 * location['available'] /
                                           float(total)})
        data.update({'locations': locations,
                     'headers': list(sort_headers.headers()),
                     'use_sorttable': True,
                    })

    return render_to_response('uptake.html', data, context_instance =
                              RequestContext(request))

@login_required
def lstats(request):
    """Location Statistics"""
    if request.GET.get('p'):
        # using the same form as Uptake for now.
        form = UptakeForm(request.GET)
    else:
        form = UptakeForm()
    data = {'form': form}

    if form.is_bound:
        sort_headers = SortHeaders(request, LOCATION_STATS_LIST_HEADERS)
        products = [ int(p) for p in form.data.getlist('p') ]
        locations = LocationMirrorMap.objects \
            .filter(location__product__id__in=products) \
            .values('active', 'mirror__name', 'mirror__baseurl',
                    'location__path') \
            .order_by(sort_headers.get_order_by())
        data.update({'locations': locations,
                     'headers': list(sort_headers.headers()),
                     'use_sorttable': True,
                    })
    return render_to_response('lstats.html', data, context_instance =
                              RequestContext(request))

