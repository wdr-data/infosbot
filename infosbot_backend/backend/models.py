import datetime

from django.db import models
from django.utils import timezone


class Info(models.Model):

    class Meta:
        verbose_name = 'Info'
        verbose_name_plural = 'Infos'

    headline = models.CharField('Schlagzeile', max_length=200, null=False)
    intro_text = models.CharField('Intro-Text', max_length=200, null=False)
    intro_media = models.FileField('Medien-Anhang Intro', null=True, blank=True)

    first_question = models.CharField('Erste Frage', max_length=20, null=True, blank=True)
    first_text = models.CharField('Erster Text', max_length=600, null=True, blank=True)
    first_media = models.FileField('Erster Medien-Anhang', null=True, blank=True)

    second_question = models.CharField('Zweite Frage', max_length=20, null=True, blank=True)
    second_text = models.CharField('Zweiter Text', max_length=600, null=True, blank=True)
    second_media = models.FileField('Zweiter Medien-Anhang', null=True, blank=True)

    pub_date = models.DateTimeField('Veröffentlicht am', default=timezone.now)
    published = models.BooleanField('Veröffentlicht?', null=False, default=False)

    def __str__(self):
        return '%s - %s' % (self.pub_date.strftime('%d.%m.%Y'), self.headline)


class FacebookUser(models.Model):

    class Meta:
        verbose_name = 'Facebook User'
        verbose_name_plural = 'Facebook User'

    uid = models.CharField('User ID', max_length=64, null=False, unique=True)
    name = models.CharField('Name', max_length=64, null=True, blank=True)
    add_date = models.DateTimeField('Hinzugefügt am', default=timezone.now)

    def __str__(self):
        return '%s (%s)' % (self.name or 'Kein Name', self.uid)
