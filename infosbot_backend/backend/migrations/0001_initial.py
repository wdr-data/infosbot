# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-21 11:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(max_length=200, verbose_name='Schlagzeile')),
                ('intro_text', models.CharField(max_length=200, verbose_name='Intro-Text')),
                ('first_question', models.CharField(max_length=20, null=True, verbose_name='Erste Frage')),
                ('first_text', models.CharField(max_length=600, null=True, verbose_name='Erster Text')),
                ('second_question', models.CharField(max_length=20, null=True, verbose_name='Zweite Frage')),
                ('second_text', models.CharField(max_length=600, null=True, verbose_name='Zweiter Text')),
                ('media', models.FileField(null=True, upload_to='', verbose_name='Medien-Anhang')),
                ('pub_date', models.DateTimeField(verbose_name='Veröffentlicht am')),
            ],
        ),
    ]
