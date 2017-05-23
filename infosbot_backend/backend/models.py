import datetime
import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from bot.fb import upload_attachment

logger = logging.getLogger(__name__)


class Info(models.Model):

    class Meta:
        verbose_name = 'Info'
        verbose_name_plural = 'Infos'

    headline = models.CharField('Schlagzeile', max_length=200, null=False)
    intro_text = models.CharField('Intro-Text', max_length=200, null=False)
    intro_media = models.FileField('Medien-Anhang Intro', null=True, blank=True)
    intro_attachment_id = models.CharField(
        'Facebook Attachment ID', max_length=64, null=True, blank=True,
        help_text="Wird automatisch ausgefüllt")

    first_question = models.CharField('Erste Frage', max_length=20, null=True, blank=True)
    first_text = models.CharField('Erster Text', max_length=600, null=True, blank=True)
    first_media = models.FileField('Erster Medien-Anhang', null=True, blank=True)
    first_attachment_id = models.CharField(
        'Facebook Attachment ID', max_length=64, null=True, blank=True,
        help_text="Wird automatisch ausgefüllt")

    second_question = models.CharField('Zweite Frage', max_length=20, null=True, blank=True)
    second_text = models.CharField('Zweiter Text', max_length=600, null=True, blank=True)
    second_media = models.FileField('Zweiter Medien-Anhang', null=True, blank=True)
    second_attachment_id = models.CharField(
        'Facebook Attachment ID', max_length=64, null=True, blank=True,
        help_text="Wird automatisch ausgefüllt")

    pub_date = models.DateTimeField('Veröffentlicht am', default=timezone.now)
    published = models.BooleanField('Veröffentlicht?', null=False, default=False)

    def __str__(self):
        return '%s - %s' % (self.pub_date.strftime('%d.%m.%Y'), self.headline)


@receiver(post_save, sender=Info)
def upload_to_facebook(sender, instance, raw, using, update_fields, **kwargs):
    fields = [field for field in update_fields]
    for field_name in fields:
        field = getattr(instance, field_name)
        if field.name:
            url = "https://infos.data.wdr.de/static/media/" + str(field)
            attachment_id = upload_attachment(url)
            attachment_field_name = field_name[:-len('media')] + 'attachment_id'
            setattr(instance, attachment_field_name, attachment_id)
            instance.save(update_fields=[attachment_field_name])

        else:
            attachment_field_name = field_name[:-len('media')] + 'attachment_id'
            setattr(instance, attachment_field_name, None)
            instance.save(update_fields=[attachment_field_name])


class FacebookUser(models.Model):

    class Meta:
        verbose_name = 'Facebook User'
        verbose_name_plural = 'Facebook User'

    uid = models.CharField('User ID', max_length=64, null=False, unique=True)
    name = models.CharField('Name', max_length=64, null=True, blank=True)
    add_date = models.DateTimeField('Hinzugefügt am', default=timezone.now)


class Dialogue(models.Model):
    class Meta:
        verbose_name = 'Dialog-Schnipsel'
        verbose_name_plural = 'Dialog-Schnipsel'

    input = models.CharField('Eingabe', max_length=128, null=False, unique=True,
                             help_text="Der Eingabetext des Nutzers")
    output = models.CharField('Antwort', max_length=640, null=False, blank=False,
                              help_text="Die Antwort, die der Bot auf die Eingabe geben soll")

    def __str__(self):
        return self.input
