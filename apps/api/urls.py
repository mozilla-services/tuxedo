from django.conf.urls.defaults import *

urlpatterns = patterns('api.views',
    (r'^docs/?$', 'docindex'),
    (r'^docs/(?P<command>\w+)/?$', 'docs'),

    (r'^location_show/?$', 'location_show'),
    (r'^location_add/?$', 'location_add'),
    (r'^location_delete/?$', 'location_delete'),
    (r'^product_show/?$', 'product_show'),
    (r'^product_add/?$', 'product_add'),
    (r'^product_delete/?$', 'product_delete'),
    (r'^uptake/?$', 'uptake'),
)

