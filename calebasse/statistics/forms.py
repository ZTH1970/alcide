# -*- coding: utf-8 -*-
from django import forms
from django.forms import Form

from ajax_select import make_ajax_field

from statistics import Statistic


class BaseForm(Form):
    display_or_export = forms.BooleanField(label=u'Exporter dans un fichier', required=False, localize=True)

class OneDateForm(BaseForm):
    start_date = forms.DateField(label=u'Date', required=False, localize=True)

class TwoDatesForm(BaseForm):
    start_date = forms.DateField(label=u'Date de début', required=False, localize=True)
    end_date = forms.DateField(label=u'Date de fin', required=False, localize=True)

class AnnualActivityForm(BaseForm):
    start_date = forms.DateField(label=u"Date de l'année souhaitée", required=False, localize=True)
    participants = make_ajax_field(Statistic, 'participants', 'worker-or-group', True)

class PatientsTwoDatesForm(TwoDatesForm):
    patients = make_ajax_field(Statistic, 'patients', 'patientrecord', True)

class ParticipantsPatientsTwoDatesForm(PatientsTwoDatesForm):
    participants = make_ajax_field(Statistic, 'participants', 'worker-or-group', True)
