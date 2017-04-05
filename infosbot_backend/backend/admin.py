from django.contrib import admin
from django import forms
from .models import Info


class InfoModelForm(forms.ModelForm):
    intro_text = forms.CharField(widget=forms.Textarea)
    first_text = forms.CharField(widget=forms.Textarea)
    second_text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Info
        fields = '__all__'


class InfoAdmin(admin.ModelAdmin):
    form = InfoModelForm

# Register your models here.
admin.site.register(Info, InfoAdmin)
