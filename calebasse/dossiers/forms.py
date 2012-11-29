# -*- coding: utf-8 -*-

from datetime import date

from django import forms
from django.forms import ModelForm, Form

from models import PatientRecord
from states import STATE_CHOICES

class EditPatientRecordForm(ModelForm):
    class Meta:
        model = PatientRecord

class SearchForm(Form):
    last_name = forms.CharField(label=u'Nom', required=False)
    first_name = forms.CharField(label=u'Prénom', required=False)
    folder_id = forms.CharField(label=u'Numéro de dossier', required=False)
    social_security_id = forms.CharField(label=u"Numéro d'assuré social", required=False)
    states = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(attrs={'class':'checkbox_state'}),
            label=u"test",
            choices=STATE_CHOICES, initial=(0,1,2,3,4))

class StateForm(Form):
    patient_id = forms.IntegerField()
    service_id = forms.IntegerField()
    state_type = forms.CharField(max_length=40)
    date = forms.DateField(label=u'Date')
    comment = forms.CharField(label='Commentaire',
            required=False, widget=forms.Textarea)

class CivilStatusForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('first_name', 'last_name', 'birthdate', 'gender', 'nationality')

