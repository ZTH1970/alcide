from django.db import models

class Personnel(models.Model):
    pass

class Conge(models.Model):
    personne = models.ForeignKey(Personnel)

class CongeAnnuel(models.Model):
    pass
