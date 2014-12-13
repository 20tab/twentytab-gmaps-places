from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from gmaps.errors import NoResults, RequestDenied, InvalidRequest, RateLimitExceeded
from models import GmapsPlace, GmapsItem

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
        return u"<img src='{}gmaps_places/flags/blank.png' class='flag flag-{}'>".format(
            settings.STATIC_URL, obj.country_code.lower())
    country_flag.allow_tags = True

    def process_address(modeladmin, request, queryset):
        for gitem in queryset:
            try:
                gitem.process_address()
            except (NoResults, RequestDenied, InvalidRequest, RateLimitExceeded) as e:
                msg_string = u"{} for url {}. Results: {}".format(
                    e.message['status'], e.message['url'], e.message['results'])
                messages.error(request, msg_string)
            else:
                time.sleep(0.1)

    list_display = ('address', 'country', country_flag, 'geo_type')
    save_on_top = True
    actions = (process_address,)
    search_fields = [
        'country',
        'administrative_area_level_1',
        'administrative_area_level_2',
        'administrative_area_level_3',
        'administrative_area_level_4',
        'administrative_area_level_5',
        'neighborhood', 'postal_code',
        'locality', 'sublocality', 'address', 'geocode']
    fieldsets = (
        (None, {
            'fields': (
                ('address',),
                ('geocode', 'geo_type'),
                ('country', 'administrative_area_level_1',
                    'administrative_area_level_2',
                    'administrative_area_level_3',
                    'administrative_area_level_4',
                    'administrative_area_level_5',
                    'locality', 'sublocality',
                    'neighborhood', 'premise', 'subpremise',
                    'postal_code', 'natural_feature', 'airport',
                    'park', 'street_address', 'street_number',
                    'route', 'intersection',),
            )
        }
        ),
    )

    class Media:
        js = (
            settings.JQUERY_LIB,
            settings.SELECT2_LIB,
            '{}gmapsmarkers/js/gmaps.js'.format(settings.STATIC_URL),
            '{}gmapsmarkers/js/gmaps__init.js'.format(settings.STATIC_URL),
            '{}gmaps_places/gmaps_places.js'.format(settings.STATIC_URL),
        )
        css = {
            "all": (
                settings.SELECT2_CSS_LIB,
                "{}gmapsmarkers/css/gmaps.css".format(settings.STATIC_URL),
                '{}gmaps_places/flags/flags.css'.format(settings.STATIC_URL),
            )
        }


admin.site.register(GmapsPlace, GmapsPlaceAdmin)
admin.site.register(GmapsItem, GmapsItemAdmin)
