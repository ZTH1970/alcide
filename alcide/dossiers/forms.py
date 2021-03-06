# -*- coding: utf-8 -*-

import os
import logging

from datetime import date

from django import forms
from django.conf import settings
from django.forms import ModelForm, Form
import django.contrib.admin.widgets

from alcide.dossiers.models import (PatientRecord,
    PatientAddress, PatientContact, DEFAULT_ACT_NUMBER_TREATMENT,
    CmppHealthCareTreatment, CmppHealthCareDiagnostic,
    SessadHealthCareNotification, FileState, Status, ProtectionState)
from alcide.ressources.models import (HealthCenter, LargeRegime,
    CodeCFTMEA, SocialisationDuration, MDPHRequest, MDPHResponse)

from ajax_select import make_ajax_field
from django_select2.widgets import Select2MultipleWidget

logger = logging.getLogger(__name__)

class EditPatientRecordForm(ModelForm):
    class Meta:
        model = PatientRecord

class SearchForm(Form):
    last_name = forms.CharField(label=u'Nom', required=False)
    first_name = forms.CharField(label=u'Prénom', required=False)
    folder_id = forms.CharField(label=u'Numéro de dossier', required=False)
    social_security_id = forms.CharField(label=u"Numéro d'assuré social", required=False)
    states = forms.ModelMultipleChoiceField(queryset=Status.objects.all(),
            initial=Status.objects.exclude(type='CLOS'),
            widget=forms.CheckboxSelectMultiple(attrs={'class':'checkbox_state'}))

    def __init__(self, service=None, *args, **kwargs):
        self.service = service
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['states'].queryset = Status.objects.filter(services=service)


class StateForm(Form):
    patient_id = forms.IntegerField()
    service_id = forms.IntegerField()
    state_type = forms.CharField(max_length=40)
    date = forms.DateField(label=u'Date', localize=True)
    comment = forms.CharField(label='Commentaire',
            required=False, widget=forms.Textarea)

    def clean_date(self):
        patient = PatientRecord.objects.get(id=self.cleaned_data['patient_id'])
        date_selected = self.cleaned_data['date']
        current_state = patient.get_state()
        if date_selected < current_state.date_selected.date():
            raise forms.ValidationError(u"La date ne peut pas être antérieure à celle du précédent changement d'état.")
        return self.cleaned_data['date']

class PatientStateForm(ModelForm):
    date_selected = forms.DateTimeField(label=u'Date', localize=True)
    comment = forms.CharField(label='Commentaire',
            required=False, widget=forms.Textarea)

    class Meta:
        model = FileState
        fields = ('status', 'date_selected', 'comment')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 39, 'rows': 4}),
                }

    def __init__(self, service=None, *args, **kwargs):
        self.service = service
        super(PatientStateForm, self).__init__(*args, **kwargs)
        self.fields['status'].queryset = Status.objects.filter(services=service)

    def clean_date_selected(self):
        date_selected = self.cleaned_data['date_selected']
        next_state = self.instance.get_next_state()
        if self.instance.previous_state:
            if date_selected < self.instance.previous_state.date_selected:
                raise forms.ValidationError(u"La date ne peut pas être antérieure à celle du précédent changement d'état.")
        if next_state:
            if date_selected > next_state.date_selected:
                raise forms.ValidationError(u"La date ne peut pas être postérieure à celle du changement d'état suivant.")
        return self.cleaned_data['date_selected']

class NewPatientRecordForm(ModelForm):
    date_selected = forms.DateField(label=u"Date de contact", localize=True)

    def __init__(self, *args, **kwargs):
        super(NewPatientRecordForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['date_selected'].initial = date.today()

    class Meta:
        model = PatientRecord
        fields = ('last_name', 'first_name')

class GeneralForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('comment', 'pause', 'pause_comment', 'confidential')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
                'pause_comment': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
                }

class AdministrativeForm(ModelForm):
    coordinators = make_ajax_field(PatientRecord, 'coordinators', 'worker', True)
    class Meta:
        model = PatientRecord
        # ID
        fields = ('first_name', 'last_name', 'birthdate', 'birthplace',
                'gender', 'nationality',)
        # inscription
        fields += ('analysemotive', 'familymotive', 'provenance',
            'advicegiver', 'provenanceplace',)
        # out
        fields += ('outmotive', 'outto',)
        # family
        fields += ('sibship_place', 'nb_children_family', 'parental_authority',
                'family_situation', 'child_custody', 'job_mother', 'job_father',
                'rm_mother', 'rm_father', 'family_comment',)
        # transport
        fields += ('transporttype', 'transportcompany',
                  'simple_appointment_transport', 'periodic_appointment_transport',)
        # Follow up
        fields += ('coordinators', 'externaldoctor', 'externalintervener',)
        widgets = {
                'family_comment': forms.Textarea(attrs={'cols': 50, 'rows': 1}),
                }


class PhysiologyForm(ModelForm):
    cranium_perimeter = forms.DecimalField(label=u"Périmètre cranien",
                    max_digits=5, decimal_places=2, localize=True,
                    required=False)
    chest_perimeter = forms.DecimalField(label=u"Périmètre thoracique",
                    max_digits=5, decimal_places=2, localize=True,
                    required=False)

    class Meta:
        model = PatientRecord
        fields = ('size', 'weight', 'pregnancy_term',
            'cranium_perimeter', 'chest_perimeter', 'apgar_score_one',
            'apgar_score_two', 'mises_1', 'mises_2', 'mises_3',
            'deficiency_intellectual', 'deficiency_autism_and_other_ted',
            'deficiency_mental_disorder', 'deficiency_learning_disorder',
            'deficiency_auditory', 'deficiency_visual', 'deficiency_motor',
            'deficiency_metabolic_disorder', 'deficiency_brain_damage',
            'deficiency_polyhandicap', 'deficiency_behavioral_disorder',
            'deficiency_in_diagnostic', 'deficiency_other_disorder')
        widgets = {
                'mises_1': Select2MultipleWidget(attrs={'style': 'width: 32em'}),
                'mises_2': Select2MultipleWidget(attrs={'style': 'width: 32em'}),
                'mises_3': Select2MultipleWidget(attrs={'style': 'width: 32em'}),
                }


    def __init__(self, instance, **kwargs):
        super(PhysiologyForm, self).__init__(instance=instance, **kwargs)
        self.fields['mises_1'].queryset = \
                CodeCFTMEA.objects.filter(axe=1)
        self.fields['mises_2'].queryset = \
                CodeCFTMEA.objects.filter(axe=2)
        self.fields['mises_3'].queryset = \
                CodeCFTMEA.objects.filter(axe=3)


class PaperIDForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('paper_id', )

class AddrCommentForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('addresses_contacts_comment', )
        widgets = {
                'addresses_contacts_comment': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
                }

class PolicyHolderForm(ModelForm):
    class Meta:
        model = PatientRecord
        fields = ('policyholder',)
        widgets = {
                'policyholder': forms.RadioSelect(),
                }

class PatientContactForm(ModelForm):
    health_org = forms.CharField(label=u"Numéro de l'organisme destinataire", required=False)

    class Meta:
        model = PatientContact
        widgets = {
                'key': forms.TextInput(attrs={'size': 4}),
                'twinning_rank': forms.TextInput(attrs={'size': 4}),
                'health_org': forms.TextInput(attrs={'size': 9}),
                'addresses': forms.CheckboxSelectMultiple(),
                'contact_comment': forms.Textarea(attrs={'rows': 2}),
                }

    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop('patient', None)
        super(PatientContactForm, self).__init__(*args,**kwargs)
        if self.instance and self.instance.health_center:
            self.fields['health_org'].initial = self.instance.health_center.large_regime.code + self.instance.health_center.health_fund + self.instance.health_center.code
        if self.patient:
            self.fields['addresses'].queryset = self.patient.addresses
            self.fields['addresses'].required = False

    def clean(self):
        cleaned_data = super(PatientContactForm, self).clean()
        health_org = cleaned_data.get('health_org')
        other_health_center = cleaned_data.get('other_health_center')
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
                        if not other_health_center and len(health_org) == 9:
                            other_health_center = health_org[5:9]
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
                            msg = "Plusieurs centres possibles, précisez parmi :"
                            for hc in hcs:
                                msg += " %s" % str(hc)
            if msg:
                self._errors["health_org"] = self.error_class([msg])
            else:
                cleaned_data['large_regime'] = lr.code
                cleaned_data['health_center'] = hc
                cleaned_data['other_health_center'] = other_health_center
        return cleaned_data

    def save(self, commit=True):
        contact = super(PatientContactForm, self).save(commit=False)
        contact.clean()
        if commit:
            contact.save()
            if self.patient and not self.instance.addresses.all():
                self.patient.contacts.add(contact)
        return contact

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
        fields = ('start_date', 'request_date',
                'agree_date', 'insist_date', 'end_date', 'act_number',
                'prolongation', 'prolongation_date', 'comment', 'patient',
                'author')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 40, 'rows': 4}),
                'patient': forms.HiddenInput(),
                'author': forms.HiddenInput(),
                }

    def clean(self):
        cleaned_data = super(CmppHealthCareTreatmentForm, self).clean()
        if self.instance.pk and cleaned_data.get('act_number') < self.instance.get_nb_acts_cared():
            msg = u"Le nombre d'actes ne peut être inférieur au \
                nombre d'actes déja pris en charge (%d)." \
                    % self.instance.get_nb_acts_cared()
            self._errors["act_number"] = self.error_class([msg])
        return cleaned_data


class CmppHealthCareDiagnosticForm(ModelForm):
    class Meta:
        model = CmppHealthCareDiagnostic
        fields = ('start_date', 'request_date',
                'agree_date', 'insist_date', 'end_date', 'act_number',
                'comment', 'patient', 'author')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 39, 'rows': 4}),
                'patient': forms.HiddenInput(),
                'author': forms.HiddenInput(),
                }

    def clean(self):
        cleaned_data = super(CmppHealthCareDiagnosticForm, self).clean()
        if self.instance.pk and cleaned_data.get('act_number') < self.instance.get_nb_acts_cared():
            msg = u"Le nombre d'actes ne peut être inférieur au \
                nombre d'actes déja pris en charge (%d)." \
                    % self.instance.get_nb_acts_cared()
            self._errors["act_number"] = self.error_class([msg])
        return cleaned_data


class SessadHealthCareNotificationForm(ModelForm):
    class Meta:
        model = SessadHealthCareNotification
        fields = ('start_date', 'end_date',
                'request_date', 'agree_date', 'insist_date',
                'comment', 'patient', 'author')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 40, 'rows': 4}),
                'patient': forms.HiddenInput(),
                'author': forms.HiddenInput(),
                }


class SocialisationDurationForm(ModelForm):
    school = make_ajax_field(SocialisationDuration, 'school', 'school', False)
    class Meta:
        model = SocialisationDuration
        fields = ('school', 'start_date',
            'end_date', 'level', 'contact', 'comment')
        widgets = {
                'contact': forms.Textarea(attrs={'cols': 39, 'rows': 2}),
                'comment': forms.Textarea(attrs={'cols': 39, 'rows': 4}),
                }

class ProtectionStateForm(ModelForm):
    class Meta:
        model = ProtectionState
        fields = ('status', 'start_date', 'end_date', 'comment')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 39, 'rows': 4}),
                }

class MDPHRequestForm(ModelForm):
    class Meta:
        model = MDPHRequest
        fields = ('start_date', 'mdph', 'comment')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 39, 'rows': 4}),
                }

class MDPHResponseForm(ModelForm):
    class Meta:
        model = MDPHResponse
        fields = ('start_date', 'end_date', 'mdph', 'comment',
            'type_aide', 'name', 'rate')
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 39, 'rows': 4}),
                }

class AvailableRtfTemplates:
    def __iter__(self):
        if not settings.RTF_TEMPLATES_DIRECTORY:
            return iter([])
        if not os.path.exists(settings.RTF_TEMPLATES_DIRECTORY):
            logger.warning("RTF_TEMPLATES_DIRECTOR %r doesn't exist" % \
                    settings.RTF_TEMPLATES_DIRECTORY)
            return iter([])

        templates = []
        for filename in os.listdir(settings.RTF_TEMPLATES_DIRECTORY):
            templates.append((filename, filename[:-4]))
        return iter(templates)

class GenerateRtfForm(Form):
    template_filename = forms.ChoiceField(choices=AvailableRtfTemplates())
    address = forms.CharField(widget=forms.Textarea(attrs={'rows':5}), required=False)
    phone_address = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(GenerateRtfForm, self).__init__(*args, **kwargs)
        self.fields['template_filename'].choices = AvailableRtfTemplates()

class QuotationsForm(Form):

    def __init__(self, service=None, *args, **kwargs):
        self.service = service
        super(QuotationsForm, self).__init__(*args, **kwargs)
        self.fields['states'].queryset = Status.objects.filter(services=service)

    states = forms.ModelMultipleChoiceField(queryset=Status.objects.all(),
            initial=Status.objects.all(),
            widget=forms.CheckboxSelectMultiple(attrs={'class':'checkbox_state'}))
    date_actes_start = forms.DateField(label=u'Date', localize=True)
    date_actes_end = forms.DateField(label=u'Date', localize=True)
    without_quotations = forms.BooleanField()

class PatientRecordPrintForm(Form):

    prev_appointment_start_date = forms.DateField(label=u'De', required=False)
    prev_appointment_end_date = forms.DateField(label=u'au', required=False)
    next_appointment_start_date = forms.DateField(label=u'De', required=False)
    next_appointment_end_date = forms.DateField(label=u'au', required=False)
