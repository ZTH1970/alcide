# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.localflavor.fr.forms import FRPhoneNumberField, FRZipCodeField


class ServiceLinkedManager(models.Manager):
    def for_service(self, service, allow_global=True):
        '''Allows service local and service global objects'''
        return self.filter(models.Q(service=service)
                |models.Q(service__isnull=allow_global))

class ServiceLinkedModelAbstract(models.Model):
    objects = ServiceLinkedManager()
    service = models.ForeignKey('Service', null=True, blank=True)

    class Meta:
        abstract = True

class AnnexeEtablissement(ServiceLinkedModelAbstract):
    class Meta:
        verbose_name = u'Annexe d\'établissement'
        verbose_name_plural = u'Annexes d\'établissement'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=40, blank=False)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()

class CaisseAssuranceMaladie(models.Model):
    class Meta:
        verbose_name = u'Caisse d\'assurances maladie'
        verbose_name_plural = u'Caisses d\'assurances maladie'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=80)
    abbreviation = models.CharField(max_length=8)
    active = models.BooleanField(default=True)
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120, blank=True,
            null=True, default=None)
    zip_code = models.IntegerField(max_length=8)
    city = models.CharField(max_length=80)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    accounting_number = models.CharField(max_length=30)
    correspondant = models.CharField(max_length=80)


class CompagnieDeTransport(models.Model):
    class Meta:
        verbose_name = u'Compagnie de transport'
        verbose_name_plural = u'Compagnies de transport'


class CodeCFTMEA(models.Model):
    class Meta:
        verbose_name = u'Code CFTMEA'
        verbose_name_plural = u'Codes CFTMEA'


class CodeDeNonFacturation(models.Model):
    class Meta:
        verbose_name = u'Code de non-facturation'
        verbose_name_plural = u'Codes de non-facturation'


class Etablissement(ServiceLinkedModelAbstract):
    class Meta:
        verbose_name = u'Établissement'
        verbose_name_plural = u'Établissements'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=40, blank=False)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    # TODO: add this fields : finess, suite, dm, dpa, genre, categorie, statut_juridique, mft, mt, dmt

class LieuDeScolarisation(models.Model):
    class Meta:
        verbose_name = u'Lieu de scolarisation'
        verbose_name_plural = u'Lieux de scolarisation'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=70, blank=False)
    description = models.TextField()
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120, blank=True, null=True, default=None)
    zip_code = FRZipCodeField()
    city = models.CharField(max_length=80)
    phone = FRPhoneNumberField()
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    director_name = models.CharField(max_length=70)


class MotifInscription(models.Model):
    class Meta:
        verbose_name = u'Motif d\'inscription'
        verbose_name_plural = u'Motifs d\'inscription'


class Nationalite(models.Model):
    class Meta:
        verbose_name = u'Nationalité'
        verbose_name_plural = u'Nationalités'


class Profession(models.Model):
    class Meta:
        verbose_name = u'Profession'
        verbose_name_plural = u'Professions'


class Salle(models.Model):
    class Meta:
        verbose_name = u'Salles'
        verbose_name_plural = u'Salles'

class Service(models.Model):
    admin_only = True

    name = models.CharField(max_length=50)
    slug = models.SlugField()

    class Meta:
        verbose_name = u'Service'
        verbose_name_plural = u'Services'

class TarifDesSeance(models.Model):
    class Meta:
        verbose_name = u'Tarif des séances'
        verbose_name_plural = u'Tarifs des séances'


class TypeActes(models.Model):
    name = models.CharField(max_length=200)
    billable = models.BooleanField(default=True)

    class Meta:
        verbose_name = u'Type d\'actes'
        verbose_name_plural = u'Types d\'actes'


class TypeAutoriteParentale(models.Model):
    class Meta:
        verbose_name = u'Type d\'autorité parentale'
        verbose_name_plural = u'Types d\'autorités parentales'


class TypeDeConseilleur(models.Model):
    class Meta:
        verbose_name = u'Types de conseilleurs'
        verbose_name_plural = u'Types de conseilleurs'


class TypeDeGardesParentales(models.Model):
    class Meta:
        verbose_name = u'Type de gardes parentales'
        verbose_name_plural = u'Types de gardes parentales'


class TypeDeSeances(models.Model):
    class Meta:
        verbose_name = u'Type de séance'
        verbose_name_plural = u'Types de séances'


class TypeDeSituationFamiliale(models.Model):
    class Meta:
        verbose_name = u'Type de situation familiale'
        verbose_name_plural = u'Types de situations familiales'


class TypeDeTransport(models.Model):
    class Meta:
        verbose_name = u'Type de transport'
        verbose_name_plural = u'Types de transports'
