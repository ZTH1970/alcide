from django.db import models

from calebasse.personnes.models import Personne
from calebasse.ressources.models import ServiceLinkedModelAbstract

class Dossier(Personne, ServiceLinkedModelAbstract):
    pass

class ContactsPatient(Personne):
    dossier = models.ForeignKey(Dossier)
