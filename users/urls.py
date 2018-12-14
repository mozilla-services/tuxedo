import django.contrib.auth.views
from django.urls import path, re_path
from . import views

app_name = 'users'

urlpatterns = [
    path(
        r'login/', django.contrib.auth.views.LoginView.as_view(),
        name='login'),
    path(
        r'logout/',
        django.contrib.auth.views.LogoutView.as_view(),
        name='logout'),
    path(r'profile/', views.own_profile, name='profile'),
    path(r'profile/<int:pk>/', views.profile_edit, name='profile-edit'),
    path(r'users/list/', views.list, name='list'),
    path(r'profile/pwchange/',
         django.contrib.auth.views.PasswordChangeView.as_view()),
    path(r'profile/pwchange/done/',
         django.contrib.auth.views.PasswordChangeDoneView.as_view()),
    path(
        r'profile/pwreset/',
        django.contrib.auth.views.PasswordResetView.as_view(),
        name='password-reset'),
    path(r'profile/pwreset/done/',
         django.contrib.auth.views.PasswordResetDoneView.as_view()),
    re_path(r'profile/pwreset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/',
            django.contrib.auth.views.PasswordResetConfirmView.as_view()),
    path(r'profile/pwreset/complete/',
         django.contrib.auth.views.PasswordResetCompleteView.as_view()),
]
