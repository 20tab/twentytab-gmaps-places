# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import gmaps.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GmapsItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geo_type', models.CharField(max_length=100)),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=255)),
                ('short_name', models.CharField(max_length=255, blank=True)),
                ('response_json', models.TextField(blank=True)),
                ('use_viewport', models.BooleanField(default=True)),
                ('url', models.CharField(max_length=255, blank=True)),
                ('custom_zoom', models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GmapsPlace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=255, blank=True)),
                ('administrative_area_level_1', models.CharField(max_length=255, blank=True)),
                ('administrative_area_level_2', models.CharField(max_length=255, blank=True)),
                ('administrative_area_level_3', models.CharField(max_length=255, blank=True)),
                ('locality', models.CharField(max_length=255, blank=True)),
                ('sublocality', models.CharField(max_length=255, blank=True)),
                ('address', gmaps.fields.GmapsField(max_length=250)),
                ('geocode', models.CharField(max_length=255, blank=True)),
                ('geo_type', gmaps.fields.GeotypeField(max_length=250)),
                ('administrative_area_level_1_item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='gmapsplaces.GmapsItem', null=True)),
                ('administrative_area_level_2_item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='gmapsplaces.GmapsItem', null=True)),
                ('administrative_area_level_3_item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='gmapsplaces.GmapsItem', null=True)),
                ('continent_item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='gmapsplaces.GmapsItem', null=True)),
                ('country_item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='gmapsplaces.GmapsItem', null=True)),
                ('locality_item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='gmapsplaces.GmapsItem', null=True)),
                ('sublocality_item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='gmapsplaces.GmapsItem', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
