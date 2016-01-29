from . import conf
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from gmapsmarkers.fields import GmapsField, GeotypeField
from gmaps import Geocoding
from gmaps.errors import NoResults, RequestDenied, InvalidRequest, RateLimitExceeded
from .utils import country_to_continent  # , CONTINENTS

import json
import time
import uuid


ALLOWED_TYPES = settings.GMAPS_PLACES_ALLOWED_TYPES
URL_TYPES = settings.GMAPS_PLACES_URL_TYPES
GMAPS_DEFAULT_CLIENT_PARAMS = {
    'sensor': False,
    'use_https': True,
    'api_key': settings.GMAPS_API_KEY,
}
GMAPS_DEFAULT_GEOCODE_PARAMS = {
    'language': settings.GMAPS_LANGUAGE_CODE,
    # 'region': settings.GMAPS_REGION, TODO
}
GMAPS_DEFAULT_REVERSE_PARAMS = {
    'language': settings.GMAPS_LANGUAGE_CODE,
}
gmaps_api = Geocoding(**GMAPS_DEFAULT_CLIENT_PARAMS)


class gmaps_attempt(object):

    def __init__(self, gmaps_call):
        self.gmaps_call = gmaps_call

    def __call__(self, *args, **kwargs):
        attempts = 0
        success = False
        while success is not True and attempts < 3:
            attempts += 1
            try:
                result = self.gmaps_call(*args, **kwargs)
            except (NoResults, RequestDenied, InvalidRequest) as e:
                raise e
            except RateLimitExceeded as e:
                time.sleep(1)
                continue
            else:
                success = True
        return result


@gmaps_attempt
def gmaps_api_geocode(*args, **kwargs):
    return gmaps_api.geocode(*args, **kwargs)


@gmaps_attempt
def gmaps_api_reverse(*args, **kwargs):
    return gmaps_api.reverse(*args, **kwargs)


class GmapsItem(models.Model):
    geo_type = models.CharField(max_length=100)
    slug = models.SlugField()
    geocode = models.CharField(max_length=255)
    place_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255, blank=True)
    response_json = models.TextField(blank=True)
    use_viewport = models.BooleanField(default=True)
    url = models.CharField(max_length=255, blank=True)
    custom_zoom = models.PositiveSmallIntegerField(
        blank=True, null=True, choices=[(x, x) for x in range(1, 22)])

    @property
    def geo_address(self):
        if self.geo_type in (u"continent", u"country"):
            return unicode(self.name)
        name = self.short_name if self.short_name != "" else self.name
        geo_address = (
            u"{}, ".format(name)
            + (", ".join((self.url).split("/")[2:-1][::-1])).strip(" -,"))
        return unicode(geo_address)

    @property
    def geometry_latlng(self):
        # warnings.warn(("GmapsItem 'geometry_latlng' property is deprecated. ")
        #               ("Use 'geocode' attribute instead."))
        return self.geocode

    @property
    def lat(self):
        if self.geocode:
            return self.geocode.split(",")[0]
        return None

    @property
    def lng(self):
        if self.geocode:
            return self.geocode.split(",")[1]
        return None

    @property
    def geometry_bounds(self):
        try:
            results = (json.loads(self.response_json))
        except (ValueError, KeyError):
            return None
        else:
            try:
                bounds = results['geometry']['bounds']
            except KeyError:
                return None
            else:
                return json.dumps(bounds)

    @property
    def geometry_viewport(self):
        try:
            results = (json.loads(self.response_json))
        except (ValueError, KeyError):
            return None
        else:
            viewport = results['geometry']['viewport']
            return json.dumps(viewport)

    def get_response_json(self):
        if self.geo_type == 'continent':
            geo_type = ['continent', 'colloquial_area']
            results = gmaps_api_geocode(
                address=self.geo_address,
                **GMAPS_DEFAULT_GEOCODE_PARAMS)
        else:
            geo_type = [self.geo_type]
            try:
                results = gmaps_api_reverse(
                    float(self.lat), float(self.lng),
                    result_type=self.geo_type,
                    **GMAPS_DEFAULT_REVERSE_PARAMS)
            except NoResults:
                results = gmaps_api_reverse(
                    float(self.lat), float(self.lng),
                    **GMAPS_DEFAULT_REVERSE_PARAMS)
        for res in results:
            if any(x in geo_type for x in res['types']):
                return json.dumps(res)
        return None

    def _get_address_component(self, component):
        if self.response_json is None or self.response_json == "":
            return ""
        if self.geo_type == 'continent':
            geo_type = ['continent', 'colloquial_area']
        else:
            geo_type = [self.geo_type]
        response_json = (json.loads(self.response_json))
        for add in response_json['address_components']:
            if any(x in geo_type for x in add['types']):
                return add[component]
        return ""

    def get_short_name(self):
        return self._get_address_component('short_name')

    def get_long_name(self):
        return self._get_address_component('long_name')

    def get_place_id(self):
        if self.response_json is None or self.response_json == "":
            return ""
        response_json = (json.loads(self.response_json))
        return response_json['place_id']

    def get_geocode(self):
        if self.response_json is None or self.response_json == "":
            return ""
        res = (json.loads(self.response_json))
        lat = res['geometry']['location']['lat']
        lng = res['geometry']['location']['lng']
        return "{},{}".format(lat, lng)

    @staticmethod
    def _build_address_from_url(url):
        return ", ".join((url).split("/")[2:][::-1]).strip(" -,")
        # [2:] to skip the empty space and continent

    def _fix_url(self):
        prefix_components = self.url.split("/")[:-1]
        my_url = slugify(self.name)
        prefix_components.append(my_url)
        return "/" + "/".join(prefix_components)

    @classmethod
    def get_or_create_from_geocode(cls, lat, lng, geo_type, url='', bkp_name=''):
        try:
            response = gmaps_api_reverse(
                float(lat), float(lng), result_type=[geo_type, ],
                **GMAPS_DEFAULT_REVERSE_PARAMS)
        except NoResults:
            response = gmaps_api_reverse(
                float(lat), float(lng),
                **GMAPS_DEFAULT_REVERSE_PARAMS)
        new_gmi = None
        found = False
        for res in response:
            if geo_type in res['types']:
                found = True
                try:
                    new_gmi = GmapsItem.objects.get(place_id=res['place_id'], geo_type=geo_type)
                except GmapsItem.DoesNotExist:
                    place_id = res['place_id']
                    lat = res['geometry']['location']['lat']
                    lng = res['geometry']['location']['lng']
                    geocode = "{},{}".format(lat, lng)
                    name = None
                    short_name = None
                    slug = None
                    for addr in res['address_components']:
                        if geo_type in addr['types']:
                            name = addr['long_name']
                            short_name = addr['short_name']
                            slug = slugify(name)
                            break
                    url_to_append = "{}/{}".format(url, slug)
                    new_gmi = GmapsItem.objects.create(
                        geo_type=geo_type,
                        slug=slug,
                        geocode=geocode,
                        place_id=place_id,
                        name=name,
                        short_name=short_name,
                        response_json=json.dumps(res),
                        url=url_to_append
                    )
                else:
                    break

        if not found and geo_type == 'continent':
            country_temp = None
            for addr in response[0]['address_components']:
                if 'country' in addr['types']:
                    country_temp = addr['long_name']
                    break
            if country_temp in (None, ''):
                raise ValueError('Continent not found')
                # undefined
            else:
                continent = country_to_continent(country_temp)
                if continent is None:
                    raise NotImplementedError(
                        (u"The Country you are looking for, related to the current "
                         u"latlng '{},{}', is not in our list".format(lat, lng)))
            # set the "home-made" continent
            url += '/{}'.format(slugify(continent))
            new_gmi, create = GmapsItem.objects.get_or_create(
                geo_type='continent', name=continent,
                slug=slugify(continent), url=url,
                defaults={'place_id': str(uuid.uuid4()),
                          'geocode': "{},{}".format(lat, lng)})
        elif not found:
            response = gmaps_api_geocode(
                address=cls._build_address_from_url(url + slugify(bkp_name)),
                **GMAPS_DEFAULT_GEOCODE_PARAMS)
            for res in response:
                if geo_type in res['types']:
                    found = True
                    try:
                        new_gmi = GmapsItem.objects.get(place_id=res['place_id'],
                                                        geo_type=geo_type)
                    except GmapsItem.DoesNotExist:
                        place_id = res['place_id']
                        lat = res['geometry']['location']['lat']
                        lng = res['geometry']['location']['lng']
                        geocode = "{},{}".format(lat, lng)
                        name = None
                        short_name = None
                        slug = None
                        for addr in res['address_components']:
                            if geo_type in addr['types']:
                                name = addr['long_name']
                                short_name = addr['short_name']
                                slug = slugify(name)
                                break
                        url_to_append = "{}/{}".format(url, slug)
                        new_gmi = GmapsItem.objects.create(
                            geo_type=geo_type,
                            slug=slug,
                            geocode=geocode,
                            place_id=place_id,
                            name=name,
                            short_name=short_name,
                            response_json=json.dumps(res),
                            url=url_to_append
                        )
                    else:
                        break

        return new_gmi

    def __unicode__(self):
        return u"{}({})".format(self.slug, self.geo_type)

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        if not self.response_json:
            self.response_json = self.get_response_json()
            self.name = self.get_long_name()
            self.short_name = self.get_short_name()
            self.place_id = self.get_place_id()
            self.geocode = self.get_geocode()
        super(GmapsItem, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('place_id', 'geo_type')


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
    place_id = models.CharField(unique=True, max_length=255)
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

    @property
    def lat(self):
        return self.geocode.split(",")[0]

    @property
    def lng(self):
        return self.geocode.split(",")[1]

    def process_address(self):
        try:
            result = gmaps_api_geocode(self.address, **GMAPS_DEFAULT_GEOCODE_PARAMS)
        except NoResults:
            print("No Results for address {}".format(self))
            return
        else:
            result = result[0]

            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']
            self.geocode = u"{},{}".format(lat, lng)
            formatted_address = result['formatted_address']
            self.address = formatted_address
            self.place_id = result['place_id']
            address_components = result['address_components']
            set_types = set(ALLOWED_TYPES)
            for add in address_components:
                inters = set_types.intersection(set(add['types']))
                if inters:
                    for t in inters:
                        setattr(self, t, u"{}".format(add['long_name']))
            self.save()

    def __unicode__(self):
        return u'{}'.format(self.address)

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        # set the continent (we have to force it because continent is not an
        # administrative definition)
        try:
            continent = GmapsItem.get_or_create_from_geocode(
                self.lat, self.lng, 'continent')
        except NoResults:
            print("No Results for address {}".format(self))
        else:
            self.continent_item = continent
            url = continent.url
            # set all the other types
            for tp in URL_TYPES:
                curr_type = getattr(self, tp)
                if curr_type:
                    gmap_ent = GmapsItem.get_or_create_from_geocode(
                        self.lat, self.lng, tp, url, bkp_name=curr_type)
                    setattr(self, u"{}_item".format(tp), gmap_ent)
                    url = gmap_ent.url
                else:
                    url += '/-'

            # for tp in URL_TYPES:
            #     curr_type = getattr(self, tp)
            #     url_to_add = slugify(curr_type) if curr_type not in (None, '')\
            #         else u"-"
            #     url += '/{}'.format(url_to_add)
            #     if curr_type:
            #         gmap_ent = GmapsItem.get_or_create_from_geocode(
            #             self.lat, self.lng, tp, url)
            #         setattr(self, u"{}_item".format(tp), gmap_ent)
        finally:
            super(GmapsPlace, self).save(*args, **kwargs)

    class Meta:
        ordering = ('country', 'address')
