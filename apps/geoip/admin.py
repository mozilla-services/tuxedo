from django.contrib import admin

from geoip.models import Country, IPBlock, Region
from mirror.models import Mirror


class CountryAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'country_code', 'continent', 'region')
    list_filter = ('continent', 'region')
    ordering = ('country_name',)
admin.site.register(Country, CountryAdmin)


class IPBlockAdmin(admin.ModelAdmin):
    list_display = ('ip_start_addr', 'ip_start', 'ip_end_addr', 'ip_end',
                    'country')
    list_filter = ('country',)
    ordering = ('ip_start',)
admin.site.register(IPBlock, IPBlockAdmin)


class MirrorInline(admin.TabularInline):
    model = Mirror.regions.through


class RegionAdmin(admin.ModelAdmin):
    inlines = (MirrorInline,)
    list_display = ('name', 'mirror_count', 'ratings', 'priority', 'throttle',
                    'fallback', 'prevent_global_fallback', 'members')
    list_filter = ('priority',)
    ordering = ('name',)
admin.site.register(Region, RegionAdmin)
