twentytab-gmaps-places
=====================

**This project is no longer maintained. Check https://github.com/20tab/django-political-map instead**



A Django app on top of twentytab-gmaps and Google Maps api v3 to manage geolocation and markers with all the administrative level details.

*Note: this app is alpha version.*

## Installation

Use the following command: ```pip install twentytab-gmaps-places```

## Configuration

```py
INSTALLED_APPS = {
    ...,
    'gmapsmarkers',
    'gmaps_places'
    ...
}

GMAPS_API_KEY = "xxxxxxxxxxxxxxxxxxxx"

```

Check twentytab-gmaps for parameters' settings:
https://github.com/20tab/twentytab-gmaps

```py

STATIC_URL = u'/static/'
JQUERY_LIB = 'path_to_jquery'
SELECT2_LIB = 'path_to_select2_js'
SELECT2_CSS_LIB = 'path_to_select2_css'
GMAPS_LANGUAGE_CODE = u'en'

```

You can customize the gmaps types used to fill the
utility fields and used in your url system.
**Important**: be sure to set this parameters 
according to the gmaps types
https://developers.google.com/maps/documentation/javascript/geocoding#GeocodingAddressTypes
and gmaps_places models
https://github.com/20tab/twentytab-gmaps-places/blob/master/gmaps_places/models.py

Default values are:
```py
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
```


- Static files

Run collectstatic command or map static directory.

## Usage

myapp/models.py
```py
from django.db import models
from gmaps_places.models import GmapsPlace


class TestPlace(models.Model):
    location = models.ForeignKey(GmapsPlace)

    def __unicode__(self):
        return u"{}".format(self.location)
```

## Example
1. Create a ForeignKey to GmapsPlace in your model (e.g. as a "location" attribute)

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot1-models.png)

2. Add a location simply by typing the address and clicking on the choosen marker, the app will automatically fill the administrative fields. *(the image is not updated to the latest version)*

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot2-address.png)
    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot2b-address.png)

3. Use *geo_type* to force a specific administrative level in case of homonymous. Example: "Rome" is administrative_area_level_2, _3 and locality, but you just need administrative_area_level_2 depth.

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot3-geo_type.png)

4. Manage GmapsPlaces in their admin panels *(the image is not updated to the lates version)*

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot4-gmaps_places_admin.png)

5. Manage and customize GmapsItems in their admin panels.

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot5-gmaps_items_admin.png)
    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot5b-gmaps_items_admin.png)

6. GmapsPlace contains all the administrative info, while GmapsItem contains all the gmaps data. Remember to use 'select_related' in your queries.

    ```py
    >>> from test_places.models import TestPlace
    >>> example_place = TestPlace.objects.all().select_related('location', 'location__country_item')[0]
    >>> example_place
    <TestPlace: Via dei Fori Imperiali, Rome, Italy>
    >>> example_place.location.country_item
    <GmapsItem: italy(country)>
    >>> example_place.location.country_item.short_name
    u'IT'
    >>> example_place.location.country_item.geometry_bounds
    '{"northeast": {"lat": 47.092, "lng": 18.5205015}, "southwest": {"lat": 35.4929201, "lng": 6.6267201}}'
    ```
    Check the model definition for all the available attributes, properties, methods.

7. The app includes sprite and css to easily generate flags (http://flag-sprites.com/) otherwise the **country_code** attribute can be used in a custom flags tool.

    your_template.html
    ```django
    <link rel="stylesheet" href="{{ STATIC_URL }}flags/flags.css">
    ...
    <img src="{{ STATIC_URL }}flags/blank.png" class="flag flag-{{test_place.location.country_code|lower}}">
    ```
8. As a further utility, you can use the GmapsPlacesForm in your frontend template in order to show just the address input with a map in your form without showing the foreign-key and the utility gmaps' fields.

    ```py
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    from gmaps_places.forms import GmapsPlacesForm
    from test_places.forms import TestPlaceForm
    from gmaps_places.models import GmapsPlace
    from test_places.models import TestPlace


    def home(request):
        status = None
        if request.method == 'POST':
            gpform = GmapsPlacesForm(request.POST)
            test_places_form = TestPlaceForm(request.POST)
            if gpform.is_valid() and test_places_form.is_valid():
                place_id = gpform.cleaned_data['place_id']
                new_gp, created = GmapsPlace.objects.get_or_create(
                    place_id=place_id, defaults=gpform.cleaned_data)
                new_tp, created = TestPlace.objects.get_or_create(
                    location=new_gp, **test_places_form.cleaned_data)
                status = 'OK'
            else:
                status = 'KO'
        else:
            gpform = GmapsPlacesForm()
            test_places_form = TestPlaceForm()
        return render_to_response(
            'gptest.html',
            {'gpform': gpform, 'test_places_form': test_places_form, 'status': status},
            context_instance=RequestContext(request)
        )
    ```

    ```django
    <html>
        <head>
            <title>GmapsPlaces Test</title>
            {{gpform.media}}
        </head>
        <body>
            <h1>TEST GmapsPlaces</h1>
            <h2>Status: {{status}}</h2>
            <form method="post" action="">{% csrf_token %}
                {{test_places_form.as_p}}
                {{gpform.as_p}}
                <!-- remember to explicitly print hidden inputs if you
                     are not using the whole form rendering -->
                <p><input type="submit" value="Submit"></p>
            </form>
        </body>
    </html>
    ```
