from django.urls import path, re_path

from . import views

app_name = 'api'

urlpatterns = [
    path(r'docs/?', views.docindex, name='doc-index'),
    re_path(r'docs/(?P<command>\w+)/?$', views.docs, name='docs'),
    path(r'location_show/', views.location_show),
    path(r'location_add/', views.location_add),
    path(r'location_modify/', views.location_modify),
    path(r'location_delete/', views.location_delete),
    path(r'product_show/', views.product_show),
    path(r'product_add/', views.product_add),
    path(r'product_delete/', views.product_delete),
    path(r'product_language_add/', views.product_language_add),
    path(r'product_language_delete/', views.product_language_delete),
    path(r'uptake/', views.uptake),
    path(r'mirror_list/', views.mirror_list),
    path(r'create_update_alias/', views.create_update_alias),
]
