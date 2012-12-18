# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import query
from model_utils import Choices

from calebasse.models import PhoneNumberField, ZipCodeField

from model_utils.managers import PassThroughManager


class ServiceLinkedQuerySet(query.QuerySet):
    def for_service(self, service, allow_global=True):
        '''Allows service local and service global objects'''
        return self.filter(models.Q(service=service)
                |models.Q(service__isnull=allow_global))

ServiceLinkedManager = PassThroughManager.for_queryset_class(ServiceLinkedQuerySet)

class NamedAbstractModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Nom')

    def __unicode__(self):
        return self.name

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

class HealthCenter(NamedAbstractModel):
    class Meta:
        verbose_name = u'Centre d\'assurance maladie'
        verbose_name_plural = u'Centres d\'assurances maladie'

    def __unicode__(self):
        return self.large_regime.code + ' ' + self.health_fund + ' ' + self.code + ' ' + self.name

    code = models.CharField(verbose_name=u"Code du centre",
            max_length=4,
            null=True, blank=True)
    large_regime = models.ForeignKey('LargeRegime',
            verbose_name=u"Grand régime")
    dest_organism = models.CharField(max_length=8,
            verbose_name=u"Organisme destinataire")
    computer_center_code = models.CharField(max_length=8,
            verbose_name=u"Code centre informatique",
            null=True, default=True)
    abbreviation = models.CharField(verbose_name=u'Abbrévation',
            max_length=8,
            null=True, default=True)
    health_fund = models.CharField(verbose_name=u"Numéro de la caisse",
            max_length=3)
    active = models.BooleanField(default=True)
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120, blank=True,
            null=True, default=None)
    zip_code = models.CharField(max_length=8)
    city = models.CharField(max_length=80)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30,
            null=True, blank=True)
    email = models.EmailField(
            null=True, blank=True)
    accounting_number = models.CharField(max_length=30,
             null=True, blank=True)
    correspondant = models.CharField(max_length=80)


class LargeRegime(NamedAbstractModel):
    class Meta:
        verbose_name = u'Grand régime'
        verbose_name_plural = u'Grands régimes'

    def __unicode__(self):
        return self.code + ' ' + self.name

    code = models.CharField(verbose_name=u"Code grand régime",
            max_length=2)


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
        return self.slug

    slug = models.SlugField(verbose_name='Label')
    description = models.TextField(blank=True, null=True)

    # Contact
    phone = PhoneNumberField(verbose_name=u"Téléphone", blank=True, null=True)
    fax = PhoneNumberField(verbose_name=u"Fax", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Address
    address = models.CharField(max_length=120,
            verbose_name=u"Addresse")
    address_complement = models.CharField(max_length=120,
            blank=True,
            null=True,
            default=None,
            verbose_name=u"Complément d'addresse")
    zip_code = ZipCodeField(verbose_name=u"Code postal")
            #verbose_name=u"Code postal")
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
    description = models.TextField(blank=True, null=True, default=None)
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120,
            blank=True,
            null=True,
            default=None)
    zip_code = ZipCodeField(verbose_name=u"Code postal")
    city = models.CharField(max_length=80)
    phone = PhoneNumberField(verbose_name=u"Téléphone")
    fax = models.CharField(max_length=30,
            blank=True, null=True, default=None)
    email = models.EmailField(blank=True, null=True)
    director_name = models.CharField(max_length=70,
            blank=True, null=True, default=None)

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


class RoomQuerySet(query.QuerySet):
    def for_etablissement(self, etablissement):
        return self.filter(etablissement=etablissement)

    def for_service(self, service):
        return self.filter(etablissement__service=service)


class Room(NamedAbstractModel):
    objects = PassThroughManager.for_queryset_class(RoomQuerySet)()
    etablissement = models.ForeignKey('Office')

    class Meta:
        verbose_name = u'Salle'
        verbose_name_plural = u'Salles'

class AnalyseMotive(NamedAbstractModel, ServiceLinkedAbstractModel):
    class Meta:
        verbose_name = u"Motif analysé"
        verbose_name_plural = u"Motifs analysés"

class FamilyMotive(NamedAbstractModel, ServiceLinkedAbstractModel):
    class Meta:
        verbose_name = u"Motif familiale"
        verbose_name_plural = u"Motifs familiaux"

class AdviceGiver(NamedAbstractModel, ServiceLinkedAbstractModel):
    class Meta:
        verbose_name = u"Conseilleur"
        verbose_name_plural = u"Conseilleurs"

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

class ActTypeQuerySet(query.QuerySet):
    def for_service(self, service):
        return self.filter(service=service)

class ActType(NamedAbstractModel, ServiceLinkedAbstractModel):
    objects = PassThroughManager.for_queryset_class(ActTypeQuerySet)()
    billable = models.BooleanField(default=True, verbose_name=u"Facturable")

    class Meta(NamedAbstractModel.Meta):
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


AXIS =  Choices(
        (1, 'Axe I : catégories cliniques'),
        (2, 'Axe II : facteurs organiques'),
        (3, 'Axe II : facteurs environementaux'),
)

class CodeCFTMEA(NamedAbstractModel):
    code = models.IntegerField(verbose_name=u"Code")
    axe = models.IntegerField(verbose_name=u"Axe", choices=AXIS,
            max_length=1)

    def __unicode__(self):
        return "%d %s" % (self.code, self.name)

    class Meta:
        ordering = ['code']
