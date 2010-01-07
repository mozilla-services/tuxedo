from django.db.models import Sum
from django.shortcuts import render_to_response
from django.template import RequestContext
import django_tables as tables

from lib.sort_headers import SortHeaders
from mirror.models import LocationMirrorMap, Mirror


UPTAKE_LIST_HEADERS = (
    ('Product', 'location__product__name'),
    ('OS', 'location__os__name'),
    ('Available', 'available'),
    ('Total', None),
    ('Percentage', None)
)

def index(request):
    """Main login/index page"""
    return render_to_response('index.html', context_instance=
                              RequestContext(request))

def uptake(request):
    """Product Uptake on Mirrors"""
    sort_headers = SortHeaders(request, UPTAKE_LIST_HEADERS)
    locations = LocationMirrorMap.objects \
        .filter(location__product__name__icontains='firefox', active=True,
                mirror__active=True) \
        .values('location__id', 'location__product__name',
                'location__os__name') \
        .annotate(available=Sum('mirror__rating')) \
        .order_by(sort_headers.get_order_by())
    locations = list(locations)

    # calculate totals
    total = Mirror.objects.filter(active=True) \
            .aggregate(total=Sum('rating'))['total']
    for location in locations:
        location.update({'total': total,
                         'percentage': 100 * location['available'] /
                                       float(total)})

    data = {'locations': locations,
            'headers': list(sort_headers.headers()),
           }
    return render_to_response('uptake.html', data, context_instance =
                              RequestContext(request))

