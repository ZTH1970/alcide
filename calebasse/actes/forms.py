# -*- coding: utf-8 -*-

from django import forms

class ActSearchForm(forms.Form):
    STATES = (
            ('non-invoicable', u'Non facturable'),
            ('absent-or-canceled', u'Absent ou annulés'),
            ('lost', u'Perdus'),
            ('invoiced', u'Facturé'),
            ('last-invoicing', u'Dernière facturation'),
            ('current-invoicing', u'Facturation en cours'))

    INITIAL = [x[0] for x in STATES]

    last_name = forms.CharField(required=False)
    patient_record_id = forms.IntegerField(required=False)
    social_security_number = forms.CharField(required=False)

    doctor_name = forms.CharField(required=False)
    filters = forms.MultipleChoiceField(choices=STATES,
            widget=forms.CheckboxSelectMultiple,
            initial=INITIAL)
