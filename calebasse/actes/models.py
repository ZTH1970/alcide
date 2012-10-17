# -*- coding: utf-8 -*-

from django.db import models

from calebasse.agenda.models import Event, EventType
from calebasse.agenda.managers import EventManager

class Act(models.Model):
    act_type = models.ForeignKey('ressources.ActType',
            verbose_name=u'Type d\'acte')
    validated = models.BooleanField(blank=True,
            verbose_name=u'Validé')
    date = models.DateTimeField()
    patient = models.ForeignKey('dossiers.PatientRecord')
    transport_company = models.ForeignKey('ressources.TransportCompany',
            blank=True,
            null=True,
            verbose_name=u'Compagnie de transport')
    transport_type = models.ForeignKey('ressources.TransportType',
            blank=True,
            null=True,
            verbose_name=u'Type de transport')
    doctors = models.ManyToManyField('personnes.Worker',
            limit_choices_to={'type__intervene': True },
            verbose_name=u'Thérapeute')

class EventActManager(EventManager):

    def create_patient_appointment(self, title, patient, participants, act_type,
            service, start_datetime, end_datetime, description='', note=None,
            **rrule_params):
        """
        This method allow you to create a new patient appointment quickly

        Args:
            title: patient appointment title (str)
            patient: Patient object
            participants: List of CalebasseUser (therapists)
            act_type: ActType object
            service: Service object. Use session service by defaut
            start_datetime: datetime with the start date and time
            end_datetime: datetime with the end date and time
            freq, count, until, byweekday, rrule_params:
            follow the ``dateutils`` API (see http://labix.org/python-dateutil)

        Example:
            Look at calebasse.agenda.tests.EventTest (test_create_appointments method)
        """

        event_type, created = EventType.objects.get_or_create(
                label="patient_appointment"
                )

        act_event = EventAct.objects.create(
                title=title,
                event_type=event_type,
                patient=patient,
                act_type=act_type,
                date=start_datetime.date(),
                )

        return self._set_event(act_event, participants, description,
                services = [service], start_datetime = start_datetime, end_datetime = end_datetime,
                note = note, **rrule_params)


class EventAct(Act, Event):
    objects = EventActManager()
    room = models.ForeignKey('ressources.Room', blank=True, null=True,
            verbose_name=u'Salle')


    VALIDATION_CODE_CHOICES = (
            ('absent', u'Absent'),
            ('present', u'Présent'),
            )
    attendance = models.CharField(max_length=16,
            choices=VALIDATION_CODE_CHOICES,
            default='absent',
            verbose_name=u'Présence')
    convocation_sent = models.BooleanField(blank=True,
            verbose_name=u'Convoqué')

