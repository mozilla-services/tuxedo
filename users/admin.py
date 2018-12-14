from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import LegacyUser, User


@admin.register(LegacyUser)
class LegacyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'firstname', 'lastname', 'email', 'converted')
    ordering = ('username', )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass