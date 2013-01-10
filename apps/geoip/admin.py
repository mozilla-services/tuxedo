from django.contrib import admin
from django import forms

from geoip.models import Country, IPBlock, Region
from mirror.models import Mirror


class CountryAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'country_code', 'continent', 'region')
    list_filter = ('continent', 'region')
    ordering = ('country_name',)
admin.site.register(Country, CountryAdmin)


# Inspired by http://www.hindsightlabs.com/blog/2010/02/11/adding-extra-fields-to-a-model-form-in-djangos-admin/
class IPBlockFormAdmin(forms.ModelForm):
    ip_start_addr = forms.CharField()
    ip_end_addr = forms.CharField()

    class Meta:
        model = IPBlock

    def __init__(self, *args, **kwargs):
        super(IPBlockFormAdmin, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.initial['ip_start_addr'] = instance.ip_start_addr
            self.initial['ip_end_addr'] = instance.ip_end_addr

    def save(self, commit=True):
        model = super(IPBlockFormAdmin, self).save(commit=False)

        model.ip_start_addr = self.cleaned_data['ip_start_addr']
        model.ip_end_addr = self.cleaned_data['ip_end_addr']

        if commit:
            model.save()

        return model


class IPBlockAdmin(admin.ModelAdmin):
    form = IPBlockFormAdmin
    list_display = ('ip_start_addr', 'ip_start', 'ip_end_addr', 'ip_end',
                    'country')
    list_filter = ('country',)
    ordering = ('ip_start',)
    fields = ('ip_start_addr', 'ip_end_addr', 'country')
admin.site.register(IPBlock, IPBlockAdmin)


class MirrorInline(admin.TabularInline):
    model = Mirror.regions.through


class RegionAdmin(admin.ModelAdmin):
    inlines = (MirrorInline,)
    list_display = ('name', 'mirror_count', 'ratings', 'priority', 'throttle', 'fallback', 'prevent_global_fallback', 'members')
    list_filter = ('priority',)
    ordering = ('name',)
admin.site.register(Region, RegionAdmin)
