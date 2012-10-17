# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from calebasse.agenda.models import Event, EventType
from calebasse.ressources.models import ServiceLinkedAbstractModel

class People(models.Model):
    nom = models.CharField(max_length=128)
    prenoms = models.CharField(max_length=128, verbose_name=u'Prénom(s)')
    display_name = models.CharField(max_length=256)

    def save(self):
        self.display_nom = self.prenom + ' ' + self.nom
        super(People, self).save()

class Worker(People):
    class Meta:
        verbose_name = u'Personnel'
        verbose_name_plural = u'Personnels'

class UserPeople(ServiceLinkedAbstractModel, User):
    people = models.ForeignKey('People')

class Doctor(People, ServiceLinkedAbstractModel):
    pass

class SchoolTeacher(People):
    schools = models.ManyToManyField('ressources.School')
    role = models.ForeignKey('ressources.SchoolTeacherRole')

class Holliday(Event):
    worker = models.ForeignKey(People)

    def save(self):
        self.event_type = \
                EventType.objects.get_or_create(label=u'Congé')
        super(Conge, self).save()
        self.participants.add(self.personne)

class AnnualHollidays(Event, ServiceLinkedAbstractModel):
    pass
