# -*- coding: utf-8 -*-

from django.db import models

class Act(models.Model):

    class Meta:
        app_label = 'cale_base'

    VALIDATION_CODE_CHOICES = (
            ('AB', 'Absent'),
            ('PR', 'Présent'),
            )

    act_type = models.ForeignKey('ActType')
    convene = models.BooleanField(default=False)
    date = models.DateTimeField()
    event = models.ForeignKey('agenda.Event')
    room = models.CharField(max_length=60)
    validation_code = models.CharField(max_length=2,
            choices=VALIDATION_CODE_CHOICES,
            default='PR')
    transport = models.ForeignKey('Transport')

class ActType(models.Model):

    class Meta:
        app_label = 'cale_base'

    name = models.CharField(max_length=200)
    billable = models.BooleanField(default=True)

