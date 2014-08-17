from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from gmaps.fields import GmapsField, GeotypeField
from utils import country_to_continent, CONTINENTS

import urllib
import urllib2
import json

ALLOWED_TYPES = (
    'country', 'administrative_area_level_1',
    'administrative_area_level_2', 'administrative_area_level_3',
    'locality', 'sublocality',)


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
            results = (json.loads(self.response_json))['results'][0]
        except ValueError:
            return None
        else:
            lat = results['geometry']['location']['lat']
            lng = results['geometry']['location']['lng']
            return u"{},{}".format(lat, lng)

    @property
    def geometry_bounds(self):
        try:
            results = (json.loads(self.response_json))['results'][0]
        except ValueError:
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
            results = (json.loads(self.response_json))['results'][0]
        except ValueError:
            return None
        else:
            viewport = results['geometry']['viewport']
            return json.dumps(viewport)

    def get_response_json(self):
        location = self.geo_address
        location = urllib.quote_plus(smart_str(location))
        url = "".join(('http://maps.googleapis.com/maps/api/geocode/json',
                      '?address={}&sensor=false'.format(location)))
        response = urllib2.urlopen(url).read()
        result = json.loads(response)
        if result['status'] == 'OK':
            return response
        else:
            return ''

    def get_short_name(self):
        if self.response_json is None or self.response_json == "":
            return ""
        response_json = (json.loads(self.response_json))['results'][0]
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
    locality = models.CharField(max_length=255, blank=True)
    sublocality = models.CharField(max_length=255, blank=True)
    address = GmapsField(plugin_options={
        'geocode_field': 'geocode', 'type_field': 'geo_type',
        'allowed_types': ALLOWED_TYPES},
        select2_options={'width': '300px'},
        help_text=u"Type the address you're looking for and click on the red marker to select it.")
    geocode = models.CharField(max_length=255, blank=True)
    geo_type = GeotypeField(blank=True)

    continent_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapplace_continent_set', null=True, blank=True)
    country_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapplace_country_set', null=True, blank=True)
    administrative_area_level_1_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapplace_aal1_set', null=True, blank=True)
    administrative_area_level_2_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapplace_aal2_set', null=True, blank=True)
    administrative_area_level_3_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapplace_aal3_set', null=True, blank=True)
    locality_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapplace_locality_set', null=True, blank=True)
    sublocality_item = models.ForeignKey(
        GmapsItem, on_delete=models.SET_NULL,
        related_name='gmapplace_sublocality_set', null=True, blank=True)

    @property
    def country_code(self):
        if self.country_item:
            return self.country_item.short_name
        else:
            return ""

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
                    u"The Country you are looking for for the current address '{}' is not in our list".format(self.address))

        url += '/{}'.format(slugify(continent))
        gmap_ent, create = GmapsItem.objects.get_or_create(
            geo_type='continent', name=continent,
            slug=slugify(continent), url=url)
        self.continent_item = gmap_ent
        # set all the other types
        for tp in ALLOWED_TYPES:
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
