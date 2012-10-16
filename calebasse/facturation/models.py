from django.db import models

class Facture(models.Model):
    number = models.CharField(max_length=20)
    patient = models.ForeignKey('dossiers.Dossier')
    organization = models.ForeignKey('ressources.Etablissement')
    fund = models.ForeignKey('ressources.CaisseAssuranceMaladie')
    date = models.DateField()
    acts = models.ManyToManyField('actes.Acte')
