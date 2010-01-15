from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^docs/$', 'api.views.docindex'),
    (r'^docs/(?P<command>\w+)/$', 'api.views.docs'),
)

