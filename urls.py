from django.conf import settings
from django.conf.urls.defaults import patterns, include, handler404
from django.contrib import admin

admin.autodiscover()

# 404 handler is fine by default
handler500 = 'lib.views.server_error'  # need MEDIA_URL in 500 error.

urlpatterns = patterns(
    '',
    (r'^$', 'mirror.views.index'),
    (r'^stats/', include('mirror.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('users.urls')),
    (r'^api/', include('api.urls')),
)

# serve media files in debug mode
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns(
        '',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT
        }),
    )
