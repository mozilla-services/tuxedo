from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^docs/$', 'api.views.docindex'),
    (r'^docs/(?P<command>\w+)/$', 'api.views.docs'),

    (r'^location_show/$', 'api.views.location_show'),
    (r'^location_add/$', 'api.views.location_add'),
    (r'^location_delete/$', 'api.views.location_delete'),
    (r'^product_show/$', 'api.views.product_show'),
    (r'^product_add/$', 'api.views.product_add'),
    (r'^product_delete/$', 'api.views.product_delete'),
    (r'^uptake/$', 'api.views.uptake'),
)

