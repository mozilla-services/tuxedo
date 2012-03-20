from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^profile/$', 'users.views.own_profile'),
    (r'^profile/(?P<pk>\d+)$', 'users.views.profile_edition'),
    (r'^users/list/$', 'users.views.list'),
    (r'^profile/pwchange/$', 'django.contrib.auth.views.password_change'),
    (r'^profile/pwchange/done/$',
        'django.contrib.auth.views.password_change_done'),
    (r'^profile/pwreset/$', 'django.contrib.auth.views.password_reset'),
    (r'^profile/pwreset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^profile/pwreset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm'),
    (r'^profile/pwreset/complete/$',
        'django.contrib.auth.views.password_reset_complete'),
)

