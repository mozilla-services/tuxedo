from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^login/', 'django.contrib.auth.views.login'),
    (r'^logout/', 'django.contrib.auth.views.logout'),
    (r'^profile/', 'users.views.profile'),
)

