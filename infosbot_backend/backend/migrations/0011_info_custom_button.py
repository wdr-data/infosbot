# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-23 18:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_auto_20170523_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='custom_button',
            field=models.CharField(blank=True, help_text='Leer lassen für Standard-Text "Nächste Info"', max_length=20, null=True, verbose_name='Button-Text'),
        ),
    ]