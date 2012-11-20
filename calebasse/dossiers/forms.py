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
    last_name = forms.CharField(label=u'Nom', required=False)
    first_name = forms.CharField(label=u'Prénom', required=False)
    folder_id = forms.CharField(label=u'Numéro de dossier', required=False)
    social_security_id = forms.CharField(label=u"Numéro d'assuré social", required=False)
