from mirror.models import Mirror, OS, Product, User, Location
from django.contrib import admin

class MirrorAdmin(admin.ModelAdmin):
    list_display = ('mirror_name', 'mirror_baseurl', 'mirror_rating',
                    'mirror_active', 'mirror_count')
    list_filter = ('mirror_active',)
admin.site.register(Mirror, MirrorAdmin)

class OSAdmin(admin.ModelAdmin):
    list_display = ('os_name', 'os_priority')
    ordering = ('os_priority',)
admin.site.register(OS, OSAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_priority', 'product_count',
                    'product_active', 'product_checknow')
    list_filter = ('product_active', 'product_checknow')
    ordering = ('product_name',)
admin.site.register(Product, ProductAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('product', 'os', 'location_path', 'lang')
    list_filter = ('product', 'os', 'lang')
admin.site.register(Location, LocationAdmin)

