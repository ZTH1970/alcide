# -*- coding: utf-8 -*-

from django.db import models

from calebasse.personnes.models import People
from calebasse.ressources.models import ServiceLinkedAbstractModel

class Records(People, ServiceLinkedAbstractModel):
    class Meta:
        verbose_name = u'Dossier'
        verbose_name_plural = u'Dossiers'

    contacts = models.ManyToManyField('personnes.People',
            related_name='contact_of')
