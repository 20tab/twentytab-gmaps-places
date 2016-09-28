from django.test import TestCase
from django.conf import settings
from .models import GmapsPlace, GmapsItem
from gmaps import Geocoding
# from gmaps.errors import RateLimitExceeded
import json


class GmapsPlacesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        location1 = GmapsPlace(
            address='Pippo, Brentwood, CA 94513, USA')
        location1.process_address()
        place_in_oceania = GmapsPlace(
            address='County Drive, Wamuran QLD 4512, Australia')
        place_in_oceania.process_address()
        capena = GmapsPlace(
            address='capena, Capena, Roma, Italy')
        capena.process_address()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_gmaps_items_exists(self):
        self.assertNotEqual(GmapsItem.objects.all().count(), 0)

    def test_gmaps_items_have_place_id(self):
        for gmi in GmapsItem.objects.all():
            self.assertNotIn(gmi.place_id, ["", None])

    def test_gmaps_items_have_url(self):
        for gmi in GmapsItem.objects.all():
            self.assertNotIn(gmi.url, ["", None])

    def test_gmaps_items_have_name(self):
        for gmi in GmapsItem.objects.all():
            self.assertNotIn(gmi.name, ["", None])

    def test_items(self):
        gmi_country = GmapsItem.objects.get(short_name='US')
        pippo = GmapsPlace.objects.get(address='Pippo, Brentwood, CA 94513, USA')
        self.assertEqual(pippo.country_item, gmi_country)
        north_america = GmapsItem.objects.get(name='North America')
        self.assertEqual(pippo.continent_item, north_america)
        self.assertEqual(north_america.url, '/north-america')
        place_in_oceania = GmapsPlace.objects.get(address='County Drive, Wamuran QLD 4512, Australia')
        self.assertEqual(place_in_oceania.continent_item.name, 'Oceania')

    def test_build_address_from_url(self):
        url = '/north-america/usa/illinois/chicago'
        address = GmapsItem._build_address_from_url(url)
        self.assertEqual(address, 'chicago, illinois, usa')

    def test_no_country_places(self):
        gaza = GmapsPlace(address='Gaza')
        gaza.process_address()
        self.assertEqual(gaza.country_item, None)
        self.assertEqual(gaza.continent_item, None)

    def test_gmapsitem_url(self):
        wamuran = GmapsItem.objects.get(slug="wamuran")
        capena = GmapsItem.objects.get(slug="capena", geo_type='locality')
        self.assertEqual(wamuran.url, "/oceania/australia/queensland/-/-/wamuran")
        self.assertEqual(capena.url, "/europe/italy/lazio/metropolitan-city-of-rome/capena/capena")

    def test_json_like_geocode_call(self):
        gmaps_api = Geocoding(
            **{
                'sensor': True,
                'use_https': True,
                'api_key': u'{}'.format(settings.GMAPS_API_KEY)}
        )
        california = GmapsItem.objects.get(short_name="CA")
        california_response = california.get_response_json()
        geocode_response = gmaps_api.reverse(
            float(california.lat), float(california.lng),
            **{'language': 'en',
               'result_type': ['administrative_area_level_1']}
        )
        self.assertEqual(california_response, json.dumps(geocode_response[0]))

    def test_response_json_equivalence_adminarea_1(self):
        california = GmapsItem.objects.get(short_name="CA")
        insert_json = california.response_json
        california.response_json = ""
        california.save()
        self.assertEqual(insert_json, california.response_json)

    def test_gmaps_bug_results_type(self):
        martinsville = GmapsPlace(address="North Creek Road, Martinsville, IL 62442, USA")
        martinsville.process_address()
        self.assertEqual('Martinsville', martinsville.locality_item.name)

    def test_response_json_equivalence_locality(self):
        warmuran = GmapsItem.objects.get(slug="wamuran")
        insert_json = warmuran.response_json
        warmuran.response_json = ""
        warmuran.save()
        self.assertEqual(insert_json, warmuran.response_json)

    def test_response_json_equivalence_country(self):
        australia = GmapsItem.objects.get(slug="australia")
        insert_json = australia.response_json
        australia.response_json = ""
        australia.save()
        self.assertEqual(insert_json, australia.response_json)

    def test_response_json_equivalence_continent(self):
        oceania = GmapsItem.objects.get(slug="oceania")
        north_america = GmapsItem.objects.get(slug="north-america")
        insert_json_oceania = oceania.response_json
        insert_json_north_america = north_america.response_json
        oceania.response_json = ""
        north_america.response_json = ""
        oceania.save()
        north_america.save()
        self.assertEqual(insert_json_oceania, oceania.response_json)
        self.assertEqual(insert_json_north_america, north_america.response_json)

    def test_insert_more_places(self):
        location2 = GmapsPlace(
            address='Olympic Stadium, Viale dello Stadio Olimpico, 00135 Roma, Italy')
        location2.process_address()
        print("Stadio Flaminio address is a gmaps api BUG. https://code.google.com/p/gmaps-api-issues/issues/detail?id=8500 . We should check for fixes.")
        location3 = GmapsPlace(
            address='Stadio Flaminio, Piazza Maresciallo Pilsudski, 00196 Roma, Italy')
        location3.process_address()

    # def test_massive_gmaps_requests_fail(self):
    #     gmaps_api = Geocoding(
    #         **{
    #             'sensor': True,
    #             'use_https': True,
    #             'api_key': u''
    #         }
    #     )
    #     with self.assertRaises(RateLimitExceeded):
    #         for x in xrange(150):
    #             gmaps_api.geocode('Pippo, Brentwood, CA 94513, USA', **{'language': 'en'})

    def test_massive_gmaps_requests_ok(self):
        gmi = GmapsItem.objects.last()
        for x in xrange(100):
            gmi.get_response_json()
