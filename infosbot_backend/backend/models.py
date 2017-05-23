import datetime
import logging

from django.db import models
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
    intro_media_note = models.CharField(
        'Anmerkung', max_length=128, null=True, blank=True, help_text='z. B. Bildrechte')
    intro_attachment_id = models.CharField(
        'Facebook Attachment ID', max_length=64, null=True, blank=True,
        help_text="Wird automatisch ausgefüllt")

    first_question = models.CharField('Erste Frage', max_length=20, null=True, blank=True)
    first_text = models.CharField('Erster Text', max_length=600, null=True, blank=True)
    first_media = models.FileField('Erster Medien-Anhang', null=True, blank=True)
    first_media_note = models.CharField(
        'Anmerkung', max_length=128, null=True, blank=True, help_text='z. B. Bildrechte')
    first_attachment_id = models.CharField(
        'Facebook Attachment ID', max_length=64, null=True, blank=True,
        help_text="Wird automatisch ausgefüllt")

    second_question = models.CharField('Zweite Frage', max_length=20, null=True, blank=True)
    second_text = models.CharField('Zweiter Text', max_length=600, null=True, blank=True)
    second_media = models.FileField('Zweiter Medien-Anhang', null=True, blank=True)
    second_media_note = models.CharField(
        'Anmerkung', max_length=128, null=True, blank=True, help_text='z. B. Bildrechte')
    second_attachment_id = models.CharField(
        'Facebook Attachment ID', max_length=64, null=True, blank=True,
        help_text="Wird automatisch ausgefüllt")

    pub_date = models.DateTimeField('Veröffentlicht am', default=timezone.now)
    published = models.BooleanField('Veröffentlicht?', null=False, default=False)
    breaking = models.BooleanField(
        'Breaking?', null=False, default=False,
        help_text='Breaking-News werden außerhalb der regelmäßigen Push-Zyklen zu der angegebenen '
                  'Zeit gesendet')

    def __str__(self):
        return '%s - %s' % (self.pub_date.strftime('%d.%m.%Y'), self.headline)

    def save(self, *args, **kwargs):
        try:
            orig = Info.objects.get(id=self.id)
        except Info.DoesNotExist:
            orig = None

        fields = ('intro_media', 'first_media', 'second_media')
        updated_fields = list()

        for field_name in fields:
            field = getattr(self, field_name)
            orig_field = getattr(orig, field_name) if orig else ''

            if not orig and str(field) or str(field) != str(orig_field):
                updated_fields.append(field_name)

        super().save(*args, **kwargs)

        for field_name in updated_fields:
            field = getattr(self, field_name)
            if str(field):
                url = "https://infos.data.wdr.de/static/media/" + str(field)
                attachment_id = upload_attachment(url)
                attachment_field_name = field_name[:-len('media')] + 'attachment_id'
                setattr(self, attachment_field_name, attachment_id)

            else:
                attachment_field_name = field_name[:-len('media')] + 'attachment_id'
                setattr(self, attachment_field_name, None)

        if updated_fields:
            self.save()


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
