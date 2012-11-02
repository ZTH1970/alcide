# -*- coding: utf-8 -*-

import logging

from django.db import models
from django.contrib.auth.models import User

from calebasse.personnes.models import People
from calebasse.ressources.models import ServiceLinkedAbstractModel

logger = logging.getLogger('calebasse.dossiers')


class FileState(models.Model):

    class Meta:
        app_label = 'dossiers'

    patient = models.ForeignKey('dossiers.PatientRecord',
        verbose_name=u'Dossier patient', editable=False)
    state_name = models.CharField(max_length=150)
    created = models.DateTimeField(u'Création', auto_now_add=True)
    date_selected = models.DateTimeField()
    author = \
        models.ForeignKey(User,
        verbose_name=u'Auteur', editable=False)
    comment = models.TextField(max_length=3000, blank=True, null=True)
    previous_state = models.ForeignKey('FileState',
        verbose_name=u'Etat précédent',
        editable=False, blank=True, null=True)

    def get_next_state(self):
        try:
            return FileState.objects.get(previous_state=self)
        except:
            return None

    def save(self, **kwargs):
        self.date_selected = \
            datetime(self.date_selected.year,
                self.date_selected.month, self.date_selected.day)
        super(FileState, self).save(**kwargs)

    def __unicode__(self):
        return self.state_name + ' ' + str(self.date_selected)


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
