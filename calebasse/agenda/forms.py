# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django import forms

from calebasse.dossiers.models import PatientRecord
from calebasse.personnes.models import Worker
from calebasse.actes.models import EventAct

from ajax_select import make_ajax_field

class NewAppointmentForm(forms.ModelForm):
    time = forms.TimeField(label=u'Heure de début')
    DURATION_CHOICES = (
            (45, '45 minutes'),
    )
    duration = forms.TypedChoiceField(choices=DURATION_CHOICES,
            coerce=int, label=u'Durée')

    participants = make_ajax_field(EventAct, 'participants', 'worker', True)
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

    def save(self, commit=False):
        start_datetime = datetime.combine(self.cleaned_data['date'],
                    self.cleaned_data['time'])
        end_datetime = start_datetime + timedelta(
                minutes=self.cleaned_data['duration'])
        self.instance = EventAct.objects.create_patient_appointment(
                title='title #FIXME#',
                patient=self.cleaned_data['patient'],
                participants=self.cleaned_data['participants'],
                act_type=self.cleaned_data['act_type'],
                service=self.service,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description='description #FIXME#',
                room=self.cleaned_data['room'],
                note=None,)
        return self.instance

