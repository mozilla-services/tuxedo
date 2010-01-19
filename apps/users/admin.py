from django.contrib import admin

from models import LegacyUser


class LegacyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'firstname', 'lastname', 'email', 'converted')
    ordering = ('username',)
admin.site.register(LegacyUser, LegacyUserAdmin)

