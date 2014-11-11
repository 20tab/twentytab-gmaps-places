from . import conf
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
# from django.utils.encoding import smart_str
from gmapsmarkers.fields import GmapsField, GeotypeField
from gmaps import Geocoding
from gmaps.errors import NoResults, RequestDenied, InvalidRequest, RateLimitExceeded
from utils import country_to_continent, CONTINENTS

import json

ALLOWED_TYPES = settings.GMAPS_PLACES_ALLOWED_TYPES
URL_TYPES = settings.GMAPS_PLACES_URL_TYPES
GMAPS_DEFAULT_CLIENT_PARAMS = {
    'sensor': True,
    'use_https': True,
    'api_key': settings.GMAPS_API_KEY,
}
GMAPS_DEFAULT_GEOCODE_PARAMS = {
    'language': settings.GMAPS_LANGUAGE_CODE,
}

gmaps_api = Geocoding(**GMAPS_DEFAULT_CLIENT_PARAMS)


class GmapsItem(models.Model):
    geo_type = models.CharField(max_length=100)
    slug = models.SlugField()
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255, blank=True)
    # geocode = models.CharField(max_length=255, blank=True)
    response_json = models.TextField(blank=True)
    use_viewport = models.BooleanField(default=True)
    url = models.CharField(max_length=255, blank=True)
    custom_zoom = models.PositiveSmallIntegerField(
        blank=True, null=True, choices=[(x, x) for x in xrange(1, 22)])

    @property
    def geo_address(self):
        if self.geo_type in (u"continent", u"country"):
            return self.name
        name = self.short_name if self.short_name != "" else self.name
        geo_address = (", ".join((self.url).split("/")[2:-1]))\
            .strip(" -,") + u", {}".format(name)
        return geo_address

    @property
    def geometry_latlng(self):
        try:
            results = (json.loads(self.response_json))[0]
        except (ValueError, KeyError):
            return None
        else:
            lat = results['geometry']['location']['lat']
            lng = results['geometry']['location']['lng']
            return u"{},{}".format(lat, lng)

    @property
    def geometry_bounds(self):
        try:
            results = (json.loads(self.response_json))[0]
        except (ValueError, KeyError):
            return None
        else:
            try:
                bounds = results['geometry']['bounds']
            except KeyError:
                return None
            else:
                return json.dumps(bounds)
                # return u"{}".format(bounds,)

    @property
    def geometry_viewport(self):
        try:
            results = (json.loads(self.response_json))[0]
        except (ValueError, KeyError):
            return None
        else:
            viewport = results['geometry']['viewport']
            return json.dumps(viewport)

    def get_response_json(self):
        result = gmaps_api.geocode(self.geo_address, **GMAPS_DEFAULT_GEOCODE_PARAMS)
        if result:
            return json.dumps(result)
        else:
            return ''

    def get_short_name(self):
        if self.response_json is None or self.response_json == "":
            return ""
        response_json = (json.loads(self.response_json))[0]
        for add in response_json['address_components']:
            if self.geo_type in add['types']:
                return add['short_name']
        return ""

    def __unicode__(self):
        return u"{}({})".format(self.slug, self.geo_type)

    def save(self, *args, **kwargs):
        if not self.response_json:
            self.response_json = self.get_response_json()
            self.short_name = self.get_short_name()

        super(GmapsItem, self).save(*args, **kwargs)


class GmapsPlace(models.Model):
    country = models.CharField(max_length=255, blank=True)
    administrative_area_level_1 = models.CharField(max_length=255, blank=True)
    administrative_area_level_2 = models.CharField(max_length=255, blank=True)
    administrative_area_level_3 = models.CharField(max_length=255, blank=True)
    administrative_area_level_4 = models.CharField(max_length=255, blank=True)
    administrative_area_level_5 = models.CharField(max_length=255, blank=True)
    locality = models.CharField(max_length=255, blank=True)
    sublocality = models.CharField(max_length=255, blank=True)
    neighborhood = models.CharField(max_length=255, blank=True)
    premise = models.CharField(max_length=255, blank=True)
    subpremise = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    natural_feature = models.CharField(max_length=255, blank=True)
    airport = models.CharField(max_length=255, blank=True)
    park = models.CharField(max_length=255, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    street_number = models.CharField(max_length=255, blank=True)
    route = models.CharField(max_length=255, blank=True)
    intersection = models.CharField(max_length=255, blank=True)
    address = GmapsField(plugin_options={
        'geocode_field': 'geocode', 'type_field': 'geo_type',
        'allowed_types': ALLOWED_TYPES},
        select2_options={'width': '300px'},
        help_text=(u"Type the address you're looking for and click "
                   u"on the red marker to select it."))
    geocode = models.CharField(max_length=255, blank=True)
    geo_type = GeotypeField(blank=True)

    continent_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_continent_set', null=True, blank=True)
    country_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_country_set', null=True, blank=True)
    administrative_area_level_1_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_aal1_set', null=True, blank=True)
    administrative_area_level_2_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_aal2_set', null=True, blank=True)
    administrative_area_level_3_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_aal3_set', null=True, blank=True)
    administrative_area_level_4_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_aal4_set', null=True, blank=True)
    administrative_area_level_5_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_aal5_set', null=True, blank=True)
    locality_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_locality_set', null=True, blank=True)
    sublocality_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_sublocality_set', null=True, blank=True)
    neighborhood_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_neighborhood_set', null=True, blank=True)
    postal_code_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapsplace_postal_code_set', null=True, blank=True)

    @property
    def country_code(self):
        if self.country_item:
            return self.country_item.short_name
        else:
            return ""

    def process_address(self):
        try:
            result = gmaps_api.geocode(self.address, **GMAPS_DEFAULT_GEOCODE_PARAMS)
        except (NoResults, RequestDenied, InvalidRequest, RateLimitExceeded) as e:
            raise e
        else:
            lat = result[0]['geometry']['location']['lat']
            lng = result[0]['geometry']['location']['lng']
            self.geocode = u"{},{}".format(lat, lng)
            formatted_address = result[0]['formatted_address']
            self.address = formatted_address
            address_components = result[0]['address_components']
            set_types = set(ALLOWED_TYPES)
            for add in address_components:
                inters = set_types.intersection(set(add['types']))
                if inters:
                    for t in inters:
                        setattr(self, t, u"{}".format(add['long_name']))
            self.save()

    def __unicode__(self):
        return u'{}'.format(self.address)

    def save(self, *args, **kwargs):
        url = ''
        if self.country in (None, u""):
            if slugify(self.address.lower()) in [x[0] for x in CONTINENTS]:
                continent = self.address
            else:
                continent = u'undefined'
        else:
            continent = country_to_continent(self.country)
            if continent is None:
                raise NotImplementedError(
                    (u"The Country you are looking for for the current "
                     u"address '{}' is not in our list".format(self.address)))

        url += '/{}'.format(slugify(continent))
        gmap_ent, create = GmapsItem.objects.get_or_create(
            geo_type='continent', name=continent,
            slug=slugify(continent), url=url)
        self.continent_item = gmap_ent
        # set all the other types
        for tp in URL_TYPES:
            curr_type = getattr(self, tp)
            url_to_add = slugify(curr_type) if curr_type not in (None, '')\
                else u"-"
            url += '/{}'.format(url_to_add)
            if curr_type:
                geocode = self.geocode if self.geo_type == tp else None
                gmap_ent, create = GmapsItem.objects.get_or_create(
                    geo_type=tp, name=curr_type,
                    slug=slugify(curr_type), url=url)
                gmap_ent.geocode = geocode
                gmap_ent.save()
                setattr(self, u"{}_item".format(tp), gmap_ent)
        super(GmapsPlace, self).save(*args, **kwargs)

    class Meta:
        ordering = ('country', 'address')
