from mirror.models import Mirror, OS, Product, User, Location, Lang
from django.contrib import admin


class LocationAdmin(admin.ModelAdmin):
    list_display = ('product', 'os', 'lang', 'path')
    list_filter = ('product', 'os', 'lang')
    ordering = ('product',)
admin.site.register(Location, LocationAdmin)

class MirrorAdmin(admin.ModelAdmin):
    list_display = ('active', 'rating', 'name', 'baseurl', 'count')
    list_display_links = ('name',)
    list_filter = ('active',)
    ordering = ('active',)
admin.site.register(Mirror, MirrorAdmin)

class OSAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    ordering = ('priority',)
admin.site.register(OS, OSAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'count', 'active', 'checknow')
    list_filter = ('active', 'checknow')
    ordering = ('name',)
    actions = ('mark_for_checknow',)

    def mark_for_checknow(self, request, queryset):
        """Custom action to mark a list of products for sentry checking"""
        rows_updated = queryset.update(checknow=True)
        msg = "%s project(s) marked for Sentry checking."
        self.message_user(request, msg % rows_updated)
    mark_for_checknow.short_description = "Check selected projects now with " \
                                          "Sentry"

admin.site.register(Product, ProductAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'firstname', 'lastname', 'email', 'converted')
    ordering = ('username',)
admin.site.register(User, UserAdmin)

class LangAdmin(admin.ModelAdmin):
    list_display = ('lang',)
    ordering = ('lang',)
admin.site.register(Lang, LangAdmin)

