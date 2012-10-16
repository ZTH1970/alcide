# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from calebasse.agenda.models import Event, EventType
from calebasse.ressources.models import ServiceLinkedModelAbstract

class Personne(models.Model):
    nom = models.CharField(max_length=128)
    prenoms = models.CharField(max_length=128, verbose_name=u'Prénom(s)')
    display_name = models.CharField(max_length=256)

    def save(self):
        self.display_nom = self.prenom + ' ' + self.nom
        super(Personne, self).save()

class Personnel(Personne, ServiceLinkedModelAbstract):
    user = models.ForeignKey(User, blank=True,
            null=True)

class Therapeute(Personne, ServiceLinkedModelAbstract):
    pass

class Professeur(Personne):
    ROLE_CHOICES = (
            ('principal', u'Principal'),
            ('referent', u'Référent'))
    etablissement = models.ForeignKey('ressources.Etablissement')
    role = models.CharField(choices=ROLE_CHOICES,
            max_length=10,
            default='referent')

class Conge(Event):
    worker = models.ForeignKey(Personnel)

    def save(self):
        self.event_type = \
                EventType.objects.get_or_create(label=u'Congé')
        super(Conge, self).save()
        self.participants.add(self.personne)

class CongeAnnuel(Event, ServiceLinkedModelAbstract):
    pass
