# -*- coding: utf-8 -*-

from django import forms

from calebasse.actes.models import Act
from ajax_select import make_ajax_field

class ActSearchForm(forms.Form):
    STATES = (
            ('pointe', u'Pointés'),
            ('non-pointe', u'Non pointés'),
            ('valide', u'Validés'),
            ('absent-or-canceled', u'Absent ou annulés'),
            ('is-billable', u'Facturable'),
            ('non-invoicable', u'Non facturable'),
            ('switch-billable', u'Inversion de facturabilité'),
            ('lost', u'Perdus'),
            ('pause-invoicing', u'Pause facturation'),
            ('invoiced', u'Facturé'),
#            ('current-invoicing', u'Facturation en cours')
            )

    INITIAL = [x[0] for x in STATES]

    last_name = forms.CharField(required=False)
    patient_record_id = forms.IntegerField(required=False)
    social_security_number = forms.CharField(required=False)

    doctor_name = forms.CharField(required=False)
    filters = forms.MultipleChoiceField(choices=STATES,
            widget=forms.CheckboxSelectMultiple)

class ActUpdate(forms.ModelForm):
    doctors = make_ajax_field(Act, 'doctors', 'intervenant', True)
    class Meta:
        model = Act
        fields = ('act_type', 'doctors', 'is_lost', 'pause', 'switch_billable', 'comment',
                'valide')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 52, 'rows': 4}),
                }
