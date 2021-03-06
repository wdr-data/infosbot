# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-23 12:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_auto_20170523_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='delivered',
            field=models.BooleanField(default=False, help_text='Wurde die Info bereits vom Bot versendet? Nur relevant für Breaking-News.', verbose_name='Versendet?'),
        ),
        migrations.AlterField(
            model_name='info',
            name='pub_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Für morgens auf 6:00, für abends auf 18:00 timen (Uhr-Symbol)', verbose_name='Veröffentlicht am'),
        ),
    ]
