# -*- coding: utf-8 -*-

from django.db import models

from calebasse.agenda.models import Event

class Act(models.Model):
    act_type = models.ForeignKey('ressources.ActType',
            verbose_name=u'Type d\'acte')
    validated = models.BooleanField(blank=True,
            verbose_name=u'Validé')
    date = models.DateTimeField()
    patient = models.ForeignKey('dossiers.Records')
    transport_company = models.ForeignKey('ressources.TransportCompany',
            blank=True,
            null=True,
            verbose_name=u'Compagnie de transport')
    transport_type = models.ForeignKey('ressources.TransportType',
            blank=True,
            null=True,
            verbose_name=u'Type de transport')
    doctors = models.ManyToManyField('personnes.Doctor',
            verbose_name=u'Thérapeute')

class EventAct(Act, Event):
    room = models.ForeignKey('ressources.Room', blank=True, null=True,
            verbose_name=u'Salle')
    participants = models.ManyToManyField('personnes.People',
            verbose_name=u'Participants')

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
