# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-22 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20170412_1216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='info',
            name='media',
        ),
        migrations.AddField(
            model_name='info',
            name='first_media',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Erster Medien-Anhang'),
        ),
        migrations.AddField(
            model_name='info',
            name='intro_media',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Medien-Anhang Intro'),
        ),
        migrations.AddField(
            model_name='info',
            name='published',
            field=models.BooleanField(default=False, verbose_name='Veröffentlicht?'),
        ),
        migrations.AddField(
            model_name='info',
            name='second_media',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Zweiter Medien-Anhang'),
        ),
    ]
