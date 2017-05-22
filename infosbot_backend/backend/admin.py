from django.contrib import admin
from django import forms
from .models import Info, FacebookUser


class InfoModelForm(forms.ModelForm):
    intro_text = forms.CharField(
        required=True, label="Intro-Text", widget=forms.Textarea, max_length=200)
    first_text = forms.CharField(
        required=False, label="Erster Text", widget=forms.Textarea, max_length=600)
    second_text = forms.CharField(
        required=False, label="Zweiter Text", widget=forms.Textarea, max_length=600)

    class Meta:
        model = Info
        fields = '__all__'


class InfoAdmin(admin.ModelAdmin):
    form = InfoModelForm
    date_hierarchy = 'pub_date'
    list_display = ('headline', 'pub_date')


# Register your models here.
admin.site.register(Info, InfoAdmin)
admin.site.register(FacebookUser)
