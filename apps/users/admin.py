from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from models import LegacyUser, UserProfile


class LegacyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'firstname', 'lastname', 'email', 'converted')
    ordering = ('username',)
admin.site.register(LegacyUser, LegacyUserAdmin)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    verbose_name = 'User Profile'


class UserAdmin(DjangoUserAdmin):
    """subclass for Django's built-in user admin, to include user profile"""
    inlines = [UserProfileInline]
admin.site.unregister(User)  # remove built-in admin
admin.site.register(User, UserAdmin)
