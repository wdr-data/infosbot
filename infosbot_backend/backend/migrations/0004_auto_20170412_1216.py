# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-12 10:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_auto_20170411_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookuser',
            name='uid',
            field=models.CharField(max_length=64, unique=True, verbose_name='User ID'),
        ),
    ]