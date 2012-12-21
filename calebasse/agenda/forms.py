# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django import forms

from calebasse.dossiers.models import PatientRecord
from calebasse.personnes.models import Worker
from calebasse.actes.models import EventAct
from calebasse.agenda.models import Event, EventType
from calebasse.ressources.models import ActType
from calebasse.middleware.request import get_request

from ajax_select import make_ajax_field

class NewAppointmentForm(forms.ModelForm):
    date = forms.DateField(label=u'Date')
    time = forms.TimeField(label=u'Heure de début')
    duration = forms.CharField(label=u'Durée',
            help_text=u'en minutes; vous pouvez utiliser la roulette de votre souris.')

    participants = make_ajax_field(EventAct, 'participants', 'worker-or-group', True)
    patient = make_ajax_field(EventAct, 'patient', 'patientrecord', False)

    class Meta:
        model = EventAct
        fields = (
                'date',
                'time',
                'duration',
                'patient',
                'participants',
                'room',
                'act_type',
        )


    def __init__(self, instance, service=None, **kwargs):
        self.service = None
        super(NewAppointmentForm, self).__init__(instance=instance, **kwargs)
        self.fields['date'].css = 'datepicker'
        if service:
            self.service = service
            self.fields['participants'].queryset = \
                    Worker.objects.for_service(service)
            self.fields['patient'].queryset = \
                    PatientRecord.objects.for_service(service)
            self.fields['act_type'].queryset = \
                    ActType.objects.for_service(service)

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        try:
            return int(duration)
        except:
            return None

    def save(self, commit=False):
        start_datetime = datetime.combine(self.cleaned_data['date'],
                    self.cleaned_data['time'])
        end_datetime = start_datetime + timedelta(
                minutes=self.cleaned_data['duration'])
        patient = self.cleaned_data['patient']
        creator = get_request().user
        self.instance = EventAct.objects.create_patient_appointment(
                creator=creator,
                title=patient.display_name,
                patient=patient,
                participants=self.cleaned_data['participants'],
                act_type=self.cleaned_data['act_type'],
                service=self.service,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description='',
                room=self.cleaned_data['room'],
                note=None,)
        return self.instance

class UpdateAppointmentForm(NewAppointmentForm):

    def __init__(self, instance, service=None, occurrence=None, **kwargs):
        super(UpdateAppointmentForm, self).__init__(instance=instance,
                                                    service=service, **kwargs)
        self.occurrence = occurrence


    def save(self):
        self.occurrence.start_time = datetime.combine(
                self.cleaned_data['date'],
                self.cleaned_data['time'])
        self.occurrence.end_time = self.occurrence.start_time + timedelta(
                minutes=self.cleaned_data['duration'])
        self.occurrence.save()
        patient = self.cleaned_data['patient']
        creator = get_request().user
        self.instance.title = patient.display_name
        self.instance.participants = self.cleaned_data['participants']
        self.instance.save()
        return self.instance


class NewEventForm(forms.ModelForm):

    title = forms.CharField(label=u"Complément de l'intitulé", max_length=32, required=False)
    date = forms.DateField(label=u'Date')
    time = forms.TimeField(label=u'Heure de début')
    duration = forms.CharField(label=u'Durée',
            help_text=u'en minutes; vous pouvez utiliser la roulette de votre souris.')
    participants = make_ajax_field(EventAct, 'participants', 'worker-or-group', True)

    class Meta:
        model = Event
        widgets = {'services': forms.CheckboxSelectMultiple}
        fields = (
                'title',
                'date',
                'time',
                'duration',
                'room',
                'participants',
                'services',
                'event_type'
        )

    def __init__(self, instance, **kwargs):
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

    def save(self, commit=False):
        start_datetime = datetime.combine(self.cleaned_data['date'],
                    self.cleaned_data['time'])
        end_datetime = start_datetime + timedelta(
                minutes=self.cleaned_data['duration'])
        self.instance = Event.objects.create_event(
                title=self.cleaned_data['title'],
                event_type=self.cleaned_data['event_type'],
                participants=self.cleaned_data['participants'],
                services=self.cleaned_data['services'],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description='',
                room=self.cleaned_data['room'],
                note=None,)
        return self.instance

    def clean(self):
        cleaned_data = super(NewEventForm, self).clean()
        event_type = cleaned_data.get('event_type')
        if event_type and event_type.id == 4 and not cleaned_data.get('title'): # 'Autre'
            self._errors['title'] = self.error_class([
                            u"Ce champ est obligatoire pour les événements de type « Autre »."])
        return cleaned_data


class UpdateEventForm(NewEventForm):

    def __init__(self, instance, occurrence=None, **kwargs):
        super(UpdateEventForm, self).__init__(instance=instance, **kwargs)
        self.occurrence = occurrence

    def save(self):
        self.occurrence.start_time = datetime.combine(
                self.cleaned_data['date'],
                self.cleaned_data['time'])
        self.occurrence.end_time = self.occurrence.start_time + timedelta(
                minutes=self.cleaned_data['duration'])
        self.occurrence.save()
        creator = get_request().user
        self.instance.participants = self.cleaned_data['participants']
        self.instance.services = self.cleaned_data['services']
        self.instance.save()
        return self.instance
