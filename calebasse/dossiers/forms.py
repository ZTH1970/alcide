# -*- coding: utf-8 -*-

from datetime import date

from django import forms
from django.forms import ModelForm, Form

from calebasse.dossiers.models import (PatientRecord,
    PatientAddress, PatientContact, DEFAULT_ACT_NUMBER_TREATMENT,
    CmppHealthCareTreatment, CmppHealthCareDiagnostic,
    SessadHealthCareNotification)
from calebasse.dossiers.states import STATE_CHOICES
from calebasse.ressources.models import (HealthCenter, LargeRegime)

from ajax_select import make_ajax_field


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
            choices=STATE_CHOICES, initial=(0,1,2,3,4))

class StateForm(Form):
    patient_id = forms.IntegerField()
    service_id = forms.IntegerField()
    state_type = forms.CharField(max_length=40)
    date = forms.DateField(label=u'Date')
    comment = forms.CharField(label='Commentaire',
            required=False, widget=forms.Textarea)

class NewPatientRecordForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('last_name', 'first_name')

class GeneralForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('comment', 'pause')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
                }

class CivilStatusForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('first_name', 'last_name', 'birthdate', 'gender', 'nationality')

class PhysiologyForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('size', 'weight', 'pregnancy_term')

class InscriptionForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('analysemotive', 'familymotive', 'advicegiver')
        widgets = {}

class FamilyForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('sibship_place', 'nb_children_family', 'parental_authority',
                'family_situation', 'child_custody')

class TransportFrom(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('transporttype', 'transportcompany')

class PaperIDForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('paper_id', )

class PolicyHolderForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('policyholder', )
        widgets = { 'policyholder': forms.RadioSelect() }

class FollowUpForm(ModelForm):
    coordinators = make_ajax_field(PatientRecord, 'coordinators', 'worker', True)
    class Meta:
        model = PatientRecord
        fields = ('coordinators', 'externaldoctor', 'externalintervener')

class PatientContactForm(ModelForm):
    addresses = make_ajax_field(PatientContact, 'addresses', 'addresses', True)
    health_org = forms.CharField(label=u"Numéro de l'organisme destinataire", required=False)

    class Meta:
        model = PatientContact
        widgets = {
                'contact_comment': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
                'key': forms.TextInput(attrs={'size': 4}),
                'twinning_rank': forms.TextInput(attrs={'size': 4}),
                'health_org': forms.TextInput(attrs={'size': 9}),
                }

    def __init__(self, *args, **kwargs):
        super(PatientContactForm, self).__init__(*args,**kwargs)
        if self.instance and self.instance.health_center:
            print self.instance.health_center
            self.fields['health_org'].initial = self.instance.health_center.large_regime.code + self.instance.health_center.health_fund + self.instance.health_center.code

    def clean(self):
        cleaned_data = super(PatientContactForm, self).clean()
        health_org = cleaned_data.get('health_org')
        if health_org:
            msg = None
            lr = None
            hc = None
            if len(health_org) < 5:
                msg = u"Numéro inférieur à 5 chiffres."
            else:
                try:
                    lr = LargeRegime.objects.get(code=health_org[:2])
                except:
                    msg = u"Grand régime %s inconnu." % health_org[:2]
                else:
                    hcs = HealthCenter.objects.filter(health_fund=health_org[2:5], large_regime=lr)
                    if not hcs:
                        msg = u"Caisse %s inconnue." % health_org[2:5]
                    elif len(hcs) == 1:
                        hc = hcs[0]
                    else:
                        if len(health_org) == 9:
                            hcs = hcs.filter(code=health_org[5:9])
                            if not hcs:
                                msg = u"Centre %s inconnu." % health_org[5:9]
                            elif len(hcs) == 1:
                                hc = hcs[0]
                            else:
                                msg = u"Ceci ne devrait pas arriver, %s n'est pas unique." % health_org
                        else:
                            msg = "Plusieurs centres possibles, précisez parmis :"
                            for hc in hcs:
                                msg += " %s" % str(hc)
            if msg:
                self._errors["health_org"] = self.error_class([msg])
            else:
                cleaned_data['large_regime'] = lr.code
                cleaned_data['health_center'] = hc
        return cleaned_data


class PatientAddressForm(ModelForm):

    class Meta:
        model = PatientAddress
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 40, 'rows': 4}),
                'zip_code': forms.TextInput(attrs={'size': 10}),
                'number': forms.TextInput(attrs={'size': 10}),
                }

class CmppHealthCareTreatmentForm(ModelForm):
    class Meta:
        model = CmppHealthCareTreatment
        fields = ('start_date', 'act_number',
                'prolongation', 'comment', 'patient', 'author')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 40, 'rows': 4}),
                'patient': forms.HiddenInput(),
                'author': forms.HiddenInput(),
                }

class CmppHealthCareDiagnosticForm(ModelForm):
    class Meta:
        model = CmppHealthCareDiagnostic
        fields = ('start_date', 'act_number',
                'comment', 'patient', 'author')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 39, 'rows': 4}),
                'patient': forms.HiddenInput(),
                'author': forms.HiddenInput(),
                }

class SessadHealthCareNotificationForm(ModelForm):
    class Meta:
        model = SessadHealthCareNotification
        fields = ('start_date', 'end_date',
                'comment', 'patient', 'author')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 40, 'rows': 4}),
                'patient': forms.HiddenInput(),
                'author': forms.HiddenInput(),
                }
