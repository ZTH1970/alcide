# -*- coding: utf-8 -*-

import logging

from django.db import models
from django.contrib.auth.models import User

from calebasse.personnes.models import People
from calebasse.ressources.models import ServiceLinkedAbstractModel

logger = logging.getLogger('calebasse.dossiers')


class PatientRecord(ServiceLinkedAbstractModel, People):
    class Meta:
        verbose_name = u'Dossier'
        verbose_name_plural = u'Dossiers'

    created = models.DateTimeField(u'création', auto_now_add=True)
    creator = \
        models.ForeignKey(User,
        verbose_name=u'Créateur dossier patient',
        editable=False)
    contacts = models.ManyToManyField('personnes.People',
            related_name='contact_of')
