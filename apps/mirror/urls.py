from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^uptake/$', 'mirror.views.uptake'),
    (r'^locations/$', 'mirror.views.lstats'),
    (r'^memcache/$', 'mirror.views.memcache_status'),
)
