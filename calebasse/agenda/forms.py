# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time

from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from ..dossiers.models import PatientRecord
from ..personnes.models import Worker
from ..actes.models import Act
from ..ressources.models import ActType
from ..middleware.request import get_request

from ajax_select import make_ajax_field
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from models import Event, EventWithAct, EventType

class BaseForm(forms.ModelForm):
    date = forms.DateField(label=u'Date', localize=True)
    time = forms.TimeField(label=u'Heure de début')
    duration = forms.CharField(label=u'Durée',
            help_text=u'en minutes; vous pouvez utiliser la roulette de votre souris.')
    participants = make_ajax_field(EventWithAct, 'participants', 'worker-or-group', True)


class NewAppointmentForm(BaseForm):
    patient = AutoCompleteSelectMultipleField('patientrecord')

    class Meta:
        model = EventWithAct
        fields = (
                'start_datetime',
                'date',
                'time',
                'duration',
                'patient',
                'participants',
                'ressource',
                'act_type',
                'description',
                'recurrence_periodicity',
                'recurrence_end_date'
        )
        widgets = {
                'start_datetime': forms.HiddenInput,
        }

    def __init__(self, instance, service=None, **kwargs):
        self.service = None
        super(NewAppointmentForm, self).__init__(instance=instance, **kwargs)
        self.fields['date'].css = 'datepicker'
        self.fields['participants'].required = True
        self.fields['time'].required = False
        self.fields['duration'].required = False
        if service:
            self.service = service
            self.special_types = [str(act.id) for act in ActType.objects.filter(Q(name__iexact='courriel')
                                                                                | Q(name__iexact='telephone')
                                                                                | Q(name__iexact='téléphone'))]
            self.fields['participants'].queryset = \
                    Worker.objects.for_service(service)
            self.fields['patient'].queryset = \
                    PatientRecord.objects.for_service(service)
            self.fields['act_type'].queryset = \
                    ActType.objects.for_service(service) \
                    .order_by('name')

    def clean_time(self):
        act_type = self.data.get('act_type')
        # act type is available as raw data from the post request
        if act_type in self.special_types:
            return time(8, 0)
        if self.cleaned_data['time']:
            return self.cleaned_data['time']
        raise forms.ValidationError(_(u'This field is required.'))

    def clean_duration(self):
        act_type = self.data.get('act_type')
        if act_type in self.special_types:
            return 10
        if self.cleaned_data['duration']:
            duration = self.cleaned_data['duration']
            try:
                duration = int(duration)
                if duration <= 0:
                    raise ValueError
                return duration
            except ValueError:
                raise forms.ValidationError(u'Le champ doit contenir uniquement des chiffres')
        raise forms.ValidationError(_(u'This field is required.'))

    def clean_patient(self):
        patients = self.cleaned_data['patient']
        if patients:
            return [patient for patient in PatientRecord.objects.filter(pk__in=patients)]

    def clean(self):
        cleaned_data = super(NewAppointmentForm, self).clean()
        if not cleaned_data.get('recurrence_periodicity'):
            cleaned_data['recurrence_end_date'] = None
        if cleaned_data.has_key('date') and cleaned_data.has_key('time'):
            cleaned_data['start_datetime'] = datetime.combine(cleaned_data['date'],
                    cleaned_data['time'])
        if 'patient' in cleaned_data and isinstance(cleaned_data['patient'], list):
            # nasty trick to store the list of patients and pass the form
            # validation
            cleaned_data['patients'] = cleaned_data['patient']
            cleaned_data['patient'] = cleaned_data['patient'][0]
        return cleaned_data

    def save(self, commit=True):

        patients = self.cleaned_data.pop('patients')
        for patient in patients:
            appointment = forms.save_instance(self, self._meta.model(), commit=False)
            appointment.start_datetime = datetime.combine(self.cleaned_data['date'],
                                                          self.cleaned_data['time'])
            appointment.end_datetime = appointment.start_datetime + timedelta(
                minutes=self.cleaned_data['duration'])
            appointment.creator = get_request().user
            appointment.clean()
            if commit:
                appointment.patient = patient
                appointment.save()
                self.save_m2m()
                appointment.services = [self.service]

class UpdateAppointmentForm(NewAppointmentForm):

    patient = make_ajax_field(EventWithAct, 'patient', 'patientrecord', False)

    def clean_patient(self):
        return self.cleaned_data['patient']

    def save(self, commit=True):
        appointment = super(NewAppointmentForm, self).save(commit=False)
        appointment.start_datetime = datetime.combine(self.cleaned_data['date'],
                    self.cleaned_data['time'])
        appointment.end_datetime = appointment.start_datetime + timedelta(
                minutes=self.cleaned_data['duration'])
        appointment.creator = get_request().user
        appointment.clean()
        if commit:
            appointment.save()
            self.save_m2m()
            appointment.services = [self.service]
        return appointment


class UpdatePeriodicAppointmentForm(UpdateAppointmentForm):
    patient = make_ajax_field(EventWithAct, 'patient', 'patientrecord', False)
    recurrence_periodicity = forms.ChoiceField(label=u"Périodicité",
            choices=Event.PERIODICITIES, required=True)

    def clean(self):
        '''
            Check that reccurrency bound dates
            won't exclude already_billed acts.
        '''
        cleaned_data = super(UpdatePeriodicAppointmentForm, self).clean()
        start_datetime = cleaned_data.get('start_datetime')
        if start_datetime:
            acts = Act.objects.filter(
                Q(parent_event=self.instance,
                    already_billed=True, date__lt=start_datetime) | \
                Q(parent_event__exception_to=self.instance,
                    already_billed=True, date__lt=start_datetime))
            if acts:
                self._errors['start_datetime'] = self.error_class([
                    u"La date de début doit être antérieure au premier acte déja facturé de la récurrence"])
        recurrence_end_date = cleaned_data.get('recurrence_end_date')
        if recurrence_end_date:
            acts = Act.objects.filter(
                Q(parent_event=self.instance,
                    already_billed=True, date__gt=recurrence_end_date) | \
                Q(parent_event__exception_to=self.instance,
                    already_billed=True, date__gt=recurrence_end_date))
            if acts:
                self._errors['recurrence_end_date'] = self.error_class([
                    u"La date de fin doit être postérieure au dernier acte déja facturé de la récurrence"])
        return cleaned_data

class DisablePatientAppointmentForm(UpdateAppointmentForm):

    def __init__(self, instance, service=None, **kwargs):
        super(DisablePatientAppointmentForm, self).__init__(instance,
                service, **kwargs)
        if instance and instance.pk:
            self.fields['patient'].required = False
            self.fields['patient'].widget.attrs['disabled'] = 'disabled'

    def clean_patient(self):
        instance = getattr(self, 'instance', None)
        if instance:
            return instance.patient
        else:
            return self.cleaned_data.get('patient', None)


class NewEventForm(BaseForm):
    title = forms.CharField(label=u"Complément de l'intitulé", max_length=32, required=False)

    class Meta:
        model = Event
        fields = (
                'start_datetime',
                'title',
                'date',
                'time',
                'duration',
                'ressource',
                'participants',
                'event_type',
                'services',
                'description',
                'recurrence_periodicity',
                'recurrence_end_date',
        )
        widgets = {
                'start_datetime': forms.HiddenInput,
                'services': forms.CheckboxSelectMultiple,
        }

    def __init__(self, instance, service=None, **kwargs):
        self.service = service
        super(NewEventForm, self).__init__(instance=instance, **kwargs)
        self.fields['date'].css = 'datepicker'
        self.fields['event_type'].queryset = \
                    EventType.objects.exclude(id=1).exclude(id=3).order_by('rank', 'label')

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        try:
            return int(duration)
        except:
            raise forms.ValidationError('Veuillez saisir un entier')

    def save(self, commit=True):
        event = super(NewEventForm, self).save(commit=False)
        event.start_datetime = datetime.combine(self.cleaned_data['date'],
                    self.cleaned_data['time'])
        event.end_datetime = event.start_datetime + timedelta(
                minutes=self.cleaned_data['duration'])
        event.creator = get_request().user
        event.clean()
        if commit:
            event.save()
            event.services = [self.service]
        return event

    def clean(self):
        cleaned_data = super(NewEventForm, self).clean()
        if cleaned_data.has_key('date') and cleaned_data.has_key('time'):
            cleaned_data['start_datetime'] = datetime.combine(cleaned_data['date'],
                    cleaned_data['time'])
        if not cleaned_data.get('recurrence_periodicity'):
            cleaned_data['recurrence_end_date'] = None
        event_type = cleaned_data.get('event_type')
        if event_type and event_type.id == 4 and not cleaned_data.get('title'): # 'Autre'
            self._errors['title'] = self.error_class([
                            u"Ce champ est obligatoire pour les événements de type « Autre »."])
        return cleaned_data

class UpdatePeriodicEventForm(NewEventForm):
    recurrence_periodicity = forms.ChoiceField(label=u"Périodicité",
            choices=Event.PERIODICITIES, required=True)

class UpdateEventForm(NewEventForm):
    class Meta(NewEventForm.Meta):
        fields = (
                'start_datetime',
                'title',
                'date',
                'time',
                'duration',
                'ressource',
                'participants',
                'event_type',
                'services',
        )

class PeriodicEventsSearchForm(forms.Form):
    start_date = forms.DateField(localize=True, required = False)
    end_date = forms.DateField(required=False, localize=True)

    event_type = forms.MultipleChoiceField(
            choices=(
                (0, 'Rendez-vous patient'),
                (1, 'Évènement')),
            widget=forms.CheckboxSelectMultiple,
            initial=[0,1])
    no_end_date = forms.BooleanField(label=u'Sans date de fin', required=False)
    patient = AutoCompleteSelectField('patientrecord', required=False, help_text='')
    worker = AutoCompleteSelectField('worker', required=False, help_text='')

    def clean(self):
        cleaned_data = super(PeriodicEventsSearchForm, self).clean()
        if cleaned_data.get('start_date') and cleaned_data.get('end_date'):
            if cleaned_data['start_date'] > cleaned_data['end_date']:
                raise forms.ValidationError(u'La date de début doit être antérieure à la date de fin')
        return cleaned_data
