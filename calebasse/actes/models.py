# -*- coding: utf-8 -*-
from django.db import models

from calebasse.agenda.models import Event

class Acte(models.Model):
    VALIDATION_CODE_CHOICES = (
            ('AB', u'Absent'),
            ('PR', u'Présent'),
            )

    act_type = models.ForeignKey('ressources.TypeActes')
    convene = models.BooleanField(default=False, blank=True)
    date = models.DateTimeField()
    room = models.ForeignKey('ressources.Salle')
    validation_code = models.CharField(max_length=2,
            choices=VALIDATION_CODE_CHOICES,
            default='PR')
    patient = models.ForeignKey('dossiers.Dossier')
    transport_company = models.ForeignKey('ressources.CompagnieDeTransport')
    doctors = models.ManyToManyField('personnes.Therapeute')

class ActeEvent(Acte, Event):
    pass
