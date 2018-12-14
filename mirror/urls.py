from django.urls import path

from . import views

app_name = 'mirror'
urlpatterns = [
    path(r'uptake/', views.uptake, name='uptake'),
    path(r'locations/', views.lstats, name='locations'),
]
