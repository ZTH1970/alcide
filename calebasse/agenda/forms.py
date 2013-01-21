# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django import forms

from ..dossiers.models import PatientRecord
from ..personnes.models import Worker
from ..ressources.models import ActType
from ..middleware.request import get_request

from ajax_select import make_ajax_field
from models import Event, EventWithAct, EventType

class BaseForm(forms.ModelForm):
    date = forms.DateField(label=u'Date', localize=True)
    time = forms.TimeField(label=u'Heure de début')
    duration = forms.CharField(label=u'Durée',
            help_text=u'en minutes; vous pouvez utiliser la roulette de votre souris.')
    participants = make_ajax_field(EventWithAct, 'participants', 'worker-or-group', True)


class NewAppointmentForm(BaseForm):
    patient = make_ajax_field(EventWithAct, 'patient', 'patientrecord', False)

    class Meta:
        model = EventWithAct
        fields = (
                'start_datetime',
                'date',
                'time',
                'duration',
                'patient',
                'participants',
                'room',
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
        if service:
            self.service = service
            self.fields['participants'].queryset = \
                    Worker.objects.for_service(service)
            self.fields['patient'].queryset = \
                    PatientRecord.objects.for_service(service)
            self.fields['act_type'].queryset = \
                    ActType.objects.for_service(service) \
                    .order_by('name')

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        try:
            return int(duration)
        except ValueError:
            return 0

    def clean(self):
        cleaned_data = super(NewAppointmentForm, self).clean()
        if not cleaned_data.get('recurrence_periodicity'):
            cleaned_data['recurrence_end_date'] = None
        if cleaned_data.has_key('date') and cleaned_data.has_key('time'):
            cleaned_data['start_datetime'] = datetime.combine(cleaned_data['date'],
                    cleaned_data['time'])
        return cleaned_data

    def save(self, commit=True):
        appointment = super(NewAppointmentForm, self).save(commit=False)
        appointment.start_datetime = datetime.combine(self.cleaned_data['date'],
                    self.cleaned_data['time'])
        appointment.end_datetime = appointment.start_datetime + timedelta(
                minutes=self.cleaned_data['duration'])
        appointment.creator = get_request().user
        appointment.title = appointment.patient.display_name
        appointment.clean()
        if commit:
            appointment.save()
            appointment.services = [self.service]
        return appointment


class UpdateAppointmentForm(NewAppointmentForm):
    class Meta(NewAppointmentForm.Meta):
        fields = (
                'start_datetime',
                'date',
                'time',
                'duration',
                'patient',
                'participants',
                'room',
                'act_type',
        )


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
                'room',
                'participants',
                'event_type',
                'services',
                'description',
                'recurrence_periodicity',
                'recurrence_end_date'
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
            return None

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


class UpdateEventForm(NewEventForm):
    class Meta(NewEventForm.Meta):
        fields = (
                'start_datetime',
                'title',
                'date',
                'time',
                'duration',
                'room',
                'participants',
                'event_type',
                'services',
        )

class PeriodicEventsSearchForm(forms.Form):
    start_date = forms.DateField(required=True, localize=True)
    end_date = forms.DateField(required=False, localize=True)

    def clean(self):
        cleaned_data = super(PeriodicEventsSearchForm, self).clean()
        if cleaned_data.get('start_date') and cleaned_data.get('end_date'):
            if cleaned_data['start_date'] > cleaned_data['end_date']:
                raise forms.ValidationError(u'La date de début doit être supérieure à la date de fin')
        return cleaned_data
