from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^docs/$', 'api.views.docs'),
    (r'^docs/(?P<command>\w+)/$', 'api.views.docs'),
)

