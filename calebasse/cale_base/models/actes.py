# -*- coding: utf-8 -*-

from django.db import models

class Act(models.Model):

    class Meta:
        app_label = 'cale_base'

    STATUS_CHOICES = (
            ('AB', 'Absent'),
            ('PR', 'Présent'),
            )

    act_type = models.ForeignKey('ActType')
    status = models.CharField(max_length=2,
            choices=STATUS_CHOICES,
            default='PR'
            )

class ActType(models.Model):

    class Meta:
        app_label = 'cale_base'

    name = models.CharField(max_length=200)

