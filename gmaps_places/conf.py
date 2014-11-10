from appconf import AppConf
from django.conf import settings


class GmapsConf(AppConf):
    GMAPS_PLACES_ALLOWED_TYPES = (
        'country', 'administrative_area_level_1',
        'administrative_area_level_2', 'administrative_area_level_3',
        'administrative_area_level_4', 'administrative_area_level_5',
        'locality', 'sublocality', 'neighborhood', 'premise', 'subpremise',
        'postal_code', 'natural_feature', 'airport', 'park',
        'street_address', 'route', 'intersection')

    GMAPS_PLACES_URL_TYPES = (
        'country', 'administrative_area_level_1',
        'administrative_area_level_2', 'administrative_area_level_3',
        'locality', 'sublocality')

    def configure_gmaps_places_allowed_types(self, value):
        if not getattr(settings, 'GMAPS_PLACES_ALLOWED_TYPES', None):
            self._meta.holder.GMAPS_PLACES_ALLOWED_TYPES = value
            return value
        return getattr(settings, 'GMAPS_PLACES_ALLOWED_TYPES')

    def configure_jquery_lib(self, value):
        if not getattr(settings, 'GMAPS_PLACES_URL_TYPES', None):
            self._meta.holder.GMAPS_PLACES_URL_TYPES = value
            return value
        return getattr(settings, 'GMAPS_PLACES_URL_TYPES')

    class Meta:
        prefix = ""
