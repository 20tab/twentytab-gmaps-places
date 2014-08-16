# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gmapsplaces', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestPlace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.ForeignKey(to='gmapsplaces.GmapsPlace')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
