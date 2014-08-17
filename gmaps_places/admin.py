from django.contrib import admin
from django.conf import settings
from gmaps_places.models import GmapsPlace, GmapsItem
import time


class GmapsItemAdmin(admin.ModelAdmin):

    def rebuild_response_json(modeladmin, request, queryset):
        queryset.update(short_name="", response_json="")
        for gitem in queryset:
            gitem.save()
            time.sleep(0.1)

    list_display = (
        'geo_type', 'slug', 'name', 'short_name', 'url',
        'geo_address', 'geometry_latlng',
        'geometry_viewport', 'geometry_bounds')
    list_filter = ('geo_type',)
    search_fields = ['slug', 'name', 'short_name', 'url', 'geo_type']
    actions = (rebuild_response_json, )


class GmapsPlaceAdmin(admin.ModelAdmin):

    def country_flag(obj):
        return u"<img src='{}flags/blank.png' class='flag flag-{}'>".format(
            settings.STATIC_URL, obj.country_code.lower())

    list_display = ('country', country_flag, 'address', 'geo_type')
    save_on_top = True
    search_fields = [
        'country',
        'administrative_area_level_1',
        'administrative_area_level_2',
        'administrative_area_level_3',
        'locality', 'sublocality', 'address', 'geocode']
    fieldsets = (
        (None, {
            'fields': (
                ('address',),
                ('geocode', 'geo_type'),
                ('country', 'administrative_area_level_1',
                    'administrative_area_level_2',
                    'administrative_area_level_3',
                    'locality', 'sublocality'),
            )
        }
        ),
    )

    class Media:
        css = {
            "all": ('{}gmaps_places/flags/flags.css'.format(settings.STATIC_URL),),
        }
        js = (
            '{}gmaps_places/gmaps_places.js'.format(settings.STATIC_URL),
        )

admin.site.register(GmapsPlace, GmapsPlaceAdmin)
admin.site.register(GmapsItem, GmapsItemAdmin)
