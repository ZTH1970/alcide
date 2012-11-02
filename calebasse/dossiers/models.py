# -*- coding: utf-8 -*-

import logging

from django.db import models

from calebasse.personnes.models import People
from calebasse.ressources.models import ServiceLinkedAbstractModel

logger = logging.getLogger('calebasse.dossiers')


class PatientRecord(ServiceLinkedAbstractModel, People):
    class Meta:
        verbose_name = u'Dossier'
        verbose_name_plural = u'Dossiers'

    contacts = models.ManyToManyField('personnes.People',
            related_name='contact_of')
