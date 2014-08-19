twentytab-gmaps-places
=====================

A django app on top of twentytab-gmaps and google maps api v3 to manage geolocation and markers with all the administrative level details.

*Note: this app is a alpha version.*

## Installation

Use the following command: ```pip install twentytab-gmaps-places```

## Configuration

```py
INSTALLED_APPS = {
    ...,
    'gmaps',
    'gmaps_places'
    ...
}

GMAPS_API_KEY = "xxxxxxxxxxxxxxxxxxxx"

```

check twentytab-gmaps for parameters' settings:
https://github.com/20tab/twentytab-gmaps

```py

STATIC_URL = u'/static/'
JQUERY_LIB = 'path_to_jquery'
SELECT2_LIB = 'path_to_select2_js'
SELECT2_CSS_LIB = 'path_to_select2_css'

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
1. Add the GmapsPlace model as FK of your location attribute

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot1-models.png)

2. Add a location simply by typing the address and clicking on the choosen marker, the app will fill the administrative fields.

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot2-address.png)
    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot2b-address.png)

3. Use *geo_type* to force a specific administrative level in case of homonymous. Example: "Rome" is administrative_area_level_2, _3 and locality, but you just need administrative_area_level_2 depth.

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot3-geo_type.png)

4. Manage GmapsPlaces in their admin panels.

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot4-gmaps_places_admin.png)

5. Manage and Customize GmapsItems in their admin panels.

    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot5-gmaps_items_admin.png)
    ![ScreenShot](https://raw.github.com/20tab/twentytab-gmaps-places/master/img/screenshot5b-gmaps_items_admin.png)

6. GmapsPlace has all the administrative infos, while GmapsItem has all the gmaps data. Remember to use 'select_related' in your query.

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
    ..and so on. Check all attributes, properties and methods available directly on the model.

7. The app includes the useful 'flags' sprite and css (http://flag-sprites.com/), so you can automatically generate flags easily (or just use **country_code** in your custom flags tool)

    your_template.html
    ```django
    <link rel="stylesheet" href="{{ STATIC_URL }}flags/flags.css">
    ...
    <img src="{{ STATIC_URL }}flags/blank.png" class="flag flag-{{test_place.location.country_code|lower}}">
    ```
