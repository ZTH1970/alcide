# -*- coding: utf-8 -*-

from django.db import models

from calebasse.models import PhoneNumberField, ZipCodeField


class ServiceLinkedManager(models.Manager):
    def for_service(self, service, allow_global=True):
        '''Allows service local and service global objects'''
        return self.filter(models.Q(service=service)
                |models.Q(service__isnull=allow_global))

class NamedAbstractModel(models.Model):
    name = models.CharField(max_length=80, verbose_name=u'Nom')

    def __unicode__(self):
        return self.name + ' (%s)' % self.id

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, unicode(self))

    class Meta:
        abstract = True
        ordering = ['name']

class ServiceLinkedAbstractModel(models.Model):
    objects = ServiceLinkedManager()
    service = models.ForeignKey('Service', null=True, blank=True)

    class Meta:
        abstract = True

# Caisse d'assurance maladie
class HealthFund(NamedAbstractModel):
    class Meta:
        verbose_name = u'Caisse d\'assurances maladie'
        verbose_name_plural = u'Caisses d\'assurances maladie'

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


class TransportCompany(NamedAbstractModel):
    class Meta:
        verbose_name = u'Compagnie de transport'
        verbose_name_plural = u'Compagnies de transport'


class CFTMEACode(NamedAbstractModel):
    class Meta:
        verbose_name = u'Code CFTMEA'
        verbose_name_plural = u'Codes CFTMEA'


class UninvoicableCode(models.Model):
    class Meta:
        verbose_name = u'Code de non-facturation'
        verbose_name_plural = u'Codes de non-facturation'


class Office(ServiceLinkedAbstractModel):
    class Meta:
        verbose_name = u'Établissement'
        verbose_name_plural = u'Établissements'

    def __unicode__(self):
        return self.name

    slug = models.SlugField()
    description = models.TextField()

    # Contact
    phone = PhoneNumberField()
    fax = PhoneNumberField()
    email = models.EmailField()

    # Address
    address = models.CharField(max_length=120,
            verbose_name=u"Addresse")
    address_complement = models.CharField(max_length=120,
            blank=True,
            null=True,
            default=None,
            verbose_name=u"Complément d'addresse")
    zip_code = ZipCodeField(
            verbose_name=u"Code postal")
    city = models.CharField(max_length=80,
            verbose_name=u"Ville")

    # TODO: add this fields : finess, suite, dm, dpa, genre, categorie, statut_juridique, mft, mt, dmt

class School(models.Model):
    class Meta:
        verbose_name = u'Lieu de scolarisation'
        verbose_name_plural = u'Lieux de scolarisation'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=70, blank=False)
    description = models.TextField()
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120,
            blank=True,
            null=True,
            default=None)
    zip_code = ZipCodeField()
    city = models.CharField(max_length=80)
    phone = PhoneNumberField()
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    director_name = models.CharField(max_length=70)

class SchoolTeacherRole(NamedAbstractModel):
    class Meta:
        verbose_name = u'Type de rôle des professeurs'
        verbose_name_plural = u'Types de rôle des professeurs'

class InscriptionMotive(NamedAbstractModel):
    class Meta:
        verbose_name = u'Motif d\'inscription'
        verbose_name_plural = u'Motifs d\'inscription'


class Nationality(NamedAbstractModel):
    class Meta:
        verbose_name = u'Nationalité'
        verbose_name_plural = u'Nationalités'


class Job(NamedAbstractModel):
    class Meta:
        verbose_name = u'Profession'
        verbose_name_plural = u'Professions'


class SalleManager(models.Manager):
    def for_etablissement(self, etablissement):
        return self.filter(etablissement=etablissement)

    def for_service(self, service):
        return self.filter(etablissement__service=service)


class Room(models.Model):
    objects = SalleManager()
    etablissement = models.ForeignKey('Office')

    class Meta:
        verbose_name = u'Salle'
        verbose_name_plural = u'Salles'


class Service(NamedAbstractModel):
    admin_only = True

    slug = models.SlugField()
    description = models.TextField()

    # Contact
    phone = PhoneNumberField(verbose_name=u"Téléphone")
    fax = PhoneNumberField(verbose_name=u"Fax")
    email = models.EmailField()

    class Meta:
        verbose_name = u'Service'
        verbose_name_plural = u'Services'


class ActType(models.Model):
    name = models.CharField(max_length=200)
    billable = models.BooleanField(default=True)

    class Meta:
        verbose_name = u'Type d\'actes'
        verbose_name_plural = u'Types d\'actes'

class ParentalAuthorityType(NamedAbstractModel):
    class Meta:
        verbose_name = u'Type d\'autorité parentale'
        verbose_name_plural = u'Types d\'autorités parentales'


class ParentalCustodyType(NamedAbstractModel):
    class Meta:
        verbose_name = u'Type de gardes parentales'
        verbose_name_plural = u'Types de gardes parentales'


class SessionType(NamedAbstractModel):
    class Meta:
        verbose_name = u'Type de séance'
        verbose_name_plural = u'Types de séances'


class FamilySituationType(NamedAbstractModel):
    class Meta:
        verbose_name = u'Type de situation familiale'
        verbose_name_plural = u'Types de situations familiales'


class TransportType(NamedAbstractModel):
    class Meta:
        verbose_name = u'Type de transport'
        verbose_name_plural = u'Types de transports'


class WorkerType(NamedAbstractModel):
    intervene = models.BooleanField(
            verbose_name=u'Intervenant',
            blank=True)

    class Meta:
        verbose_name = u'Type de personnel'
        verbose_name_plural = u'Types de personnel'

