# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form

from models import PatientRecord

class CreatePatientRecordForm(ModelForm):
    class Meta:
        model = PatientRecord


class EditPatientRecordForm(ModelForm):
    class Meta:
        model = PatientRecord

class SearchForm(Form):
    STATE_CHOICES = (
            (0, 'En contact'),
            (1, "Fin d'accueil"),
            (2, 'En diagnostic'),
            (3, 'En traitement'),
            (4, 'Clos'),
            )
    last_name = forms.CharField(label=u'Nom', required=False)
    first_name = forms.CharField(label=u'Prénom', required=False)
    folder_id = forms.CharField(label=u'Numéro de dossier', required=False)
    social_security_id = forms.CharField(label=u"Numéro d'assuré social", required=False)
    states = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=u"test",
            choices=STATE_CHOICES, initial=(0,1,2,3,4))

