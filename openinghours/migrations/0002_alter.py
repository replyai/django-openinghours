# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from ..app_settings import PREMISES_MODEL

class Migration(migrations.Migration):

    dependencies = [
        ('openinghours', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='openinghours',
            options={'ordering': ['company', 'weekday', 'from_hour'], 'verbose_name': 'Opening Hours', 'verbose_name_plural': 'Opening Hours'},
        ),
        migrations.AlterField(
            model_name='closingrules',
            name='company',
            field=models.ForeignKey(verbose_name='Company', to=PREMISES_MODEL),
        ),
        migrations.AlterField(
            model_name='openinghours',
            name='company',
            field=models.ForeignKey(verbose_name='Company', to=PREMISES_MODEL),
        ),
    ]
