from django import forms
from django.conf import settings
from gmaps_places.models import GmapsPlace

HIDDEN_FIELDS = (
    'place_id', 'country', 'administrative_area_level_1',
    'administrative_area_level_2', 'administrative_area_level_3',
    'administrative_area_level_4', 'administrative_area_level_5',
    'locality', 'sublocality', 'neighborhood', 'premise', 'subpremise',
    'postal_code', 'natural_feature', 'airport', 'park',
    'street_address', 'route', 'intersection',
    'geocode')  # , 'geo_type')


class GmapsPlacesForm(forms.ModelForm):

    place_id = forms.CharField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = GmapsPlace
        fields = [
            'address', 'country', 'administrative_area_level_1',
            'administrative_area_level_2', 'administrative_area_level_3',
            'administrative_area_level_4', 'administrative_area_level_5',
            'locality', 'sublocality', 'neighborhood', 'premise', 'subpremise',
            'postal_code', 'natural_feature', 'airport', 'park',
            'street_address', 'route', 'intersection',
            'geocode']  # , 'geo_type']
        widgets = {x: forms.HiddenInput() for x in HIDDEN_FIELDS}

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
            )
        }
