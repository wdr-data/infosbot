import datetime

from django.db import models
from django.utils import timezone


class Info(models.Model):
    headline = models.CharField('Schlagzeile', max_length=200, null=False)
    intro_text = models.CharField('Intro-Text', max_length=200, null=False)
    first_question = models.CharField('Erste Frage', max_length=20, null=True, blank=True)
    first_text = models.CharField('Erster Text', max_length=600, null=True, blank=True)
    second_question = models.CharField('Zweite Frage', max_length=20, null=True, blank=True)
    second_text = models.CharField('Zweiter Text', max_length=600, null=True, blank=True)
    media = models.FileField('Medien-Anhang', null=True, blank=True)
    pub_date = models.DateTimeField('Veröffentlicht am', default=timezone.now)

    def __str__(self):
        return '%s - %s' % (self.pub_date.strftime('%d.%m.%Y'), self.headline)
