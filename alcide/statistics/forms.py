# -*- coding: utf-8 -*-
from django import forms
from django.forms import Form
from ajax_select.fields import AutoCompleteSelectMultipleField

class BaseForm(Form):
    display_or_export = forms.BooleanField(label=u'Exporter dans un fichier', required=False, localize=True)

class OneDateForm(BaseForm):
    start_date = forms.DateField(label=u'Date', required=False, localize=True)

class TwoDatesForm(BaseForm):
    start_date = forms.DateField(label=u'Date de début', required=False, localize=True)
    end_date = forms.DateField(label=u'Date de fin', required=False, localize=True)

class AnnualActivityForm(BaseForm):
    start_date = forms.DateField(label=u"Date de l'année souhaitée", required=False, localize=True)
    participants = AutoCompleteSelectMultipleField('all-worker-or-group', required=False)

class PatientsTwoDatesForm(TwoDatesForm):
    patients = AutoCompleteSelectMultipleField('patientrecord', required=False)

class ParticipantsPatientsTwoDatesForm(PatientsTwoDatesForm):
    participants = AutoCompleteSelectMultipleField('all-worker-or-group', required=False)

class PatientsPerWorkerForPeriodForm(ParticipantsPatientsTwoDatesForm):
    no_synthesis = forms.BooleanField(label=u'Exclure les synthèses', required=False, localize=True)

class PatientsSynthesisForm(TwoDatesForm):
    inscriptions = forms.BooleanField(label=u'Seulement les inscriptions', required=False, localize=True)
