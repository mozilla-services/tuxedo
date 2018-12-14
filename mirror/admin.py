from django.contrib import admin

from mirror.models import (Mirror, OS, Product, Location, ProductLanguage,
                           ProductAlias)
from mirror.forms import ProductAliasForm


class ProductAliasAdmin(admin.ModelAdmin):
    list_display = ('alias', 'related_product')
    form = ProductAliasForm


admin.site.register(ProductAlias, ProductAliasAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('product', 'os', 'path')
    list_filter = ('product', 'os')
    ordering = ('product', )


admin.site.register(Location, LocationAdmin)


class MirrorAdmin(admin.ModelAdmin):
    exclude = ('count', )
    list_display = (
        'active',
        'rating',
        'name',
        'baseurl',
        'count',
    )
    list_display_links = ('name', )
    list_editable = ('active', )
    list_filter = ('active', )
    ordering = ('active', )
    search_fields = ['name', 'baseurl']


admin.site.register(Mirror, MirrorAdmin)


class OSAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    ordering = ('priority', )


admin.site.register(OS, OSAdmin)


class ProductLanguageInline(admin.TabularInline):
    model = ProductLanguage
    extra = 3


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'count', 'active', 'checknow',
                    'ssl_only')
    list_filter = ('active', 'checknow', 'ssl_only')
    ordering = ('name', )
    actions = ('mark_for_checknow', 'unmark_for_checknow')
    inlines = [ProductLanguageInline]

    def mark_for_checknow(self, request, queryset):
        """Custom action to mark a list of products for sentry checking"""
        rows_updated = queryset.update(checknow=True)
        msg = '%s project(s) marked for Sentry checking.'
        self.message_user(request, msg % rows_updated)

    def unmark_for_checknow(self, request, queryset):
        """Custom action to unmark a list of products for sentry checking"""
        rows_updated = queryset.update(checknow=False)
        msg = '%s project(s) no longer marked for Sentry checking.'
        self.message_user(request, msg % rows_updated)

    mark_for_checknow.short_description = (
        'Set Check Now on selected products')
    unmark_for_checknow.short_description = (
        'Remove Check Now on selected products')


admin.site.register(Product, ProductAdmin)
