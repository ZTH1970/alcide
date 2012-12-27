# -*- coding: utf-8 -*-

import logging
import os

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django import forms
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

import reversion

from calebasse.choices import LARGE_REGIME_CHOICES
from calebasse.models import PhoneNumberField, ZipCodeField
from calebasse.personnes.models import People
from calebasse.ressources.models import (ServiceLinkedAbstractModel,
        NamedAbstractModel, Service)
from calebasse.actes.validation import are_all_acts_of_the_day_locked

DEFAULT_ACT_NUMBER_DIAGNOSTIC = 6
DEFAULT_ACT_NUMBER_TREATMENT = 30
DEFAULT_ACT_NUMBER_PROLONGATION = 10
VALIDITY_PERIOD_TREATMENT_HEALTHCARE_DAYS = 0
VALIDITY_PERIOD_TREATMENT_HEALTHCARE_MONTHS = 0
VALIDITY_PERIOD_TREATMENT_HEALTHCARE_YEARS = 1

logger = logging.getLogger('calebasse.dossiers')


class HealthCare(models.Model):

    class Meta:
        app_label = 'dossiers'

    start_date = models.DateField(verbose_name=u"Date de début")
    patient = models.ForeignKey('dossiers.PatientRecord',
        verbose_name=u'Dossier patient')
    created = models.DateTimeField(u'Création', auto_now_add=True)
    author = \
        models.ForeignKey(User,
        verbose_name=u'Auteur')
    comment = models.TextField(max_length=3000, blank=True, null=True, verbose_name=u"Commentaire")

    def get_nb_acts_cared(self):
        return len(self.act_set.all())


class CmppHealthCareDiagnostic(HealthCare):

    class Meta:
        app_label = 'dossiers'

    act_number = models.IntegerField(default=DEFAULT_ACT_NUMBER_DIAGNOSTIC, verbose_name=u"Nombre d'actes couverts")

    def get_act_number(self):
        return self.act_number

    def set_act_number(self, value):
        if value < self.get_nb_acts_cared():
            raise Exception("La valeur doit être supérieur au "
                "nombre d'actes déjà pris en charge")
        self.act_number = value
        self.save()

    def save(self, **kwargs):
        self.start_date = \
            datetime(self.start_date.year, self.start_date.month,
                self.start_date.day)
        super(CmppHealthCareDiagnostic, self).save(**kwargs)


class CmppHealthCareTreatment(HealthCare):

    class Meta:
        app_label = 'dossiers'

    act_number = models.IntegerField(default=DEFAULT_ACT_NUMBER_TREATMENT,
            verbose_name=u"Nombre d'actes couverts")
    end_date = models.DateField(verbose_name=u"Date de fin")
    prolongation = models.IntegerField(default=0,
            verbose_name=u'Prolongation')

    def get_act_number(self):
        if self.is_extended():
            return self.act_number + self.prolongation
        return self.act_number

    def set_act_number(self, value):
        if value < self.get_nb_acts_cared():
            raise Exception("La valeur doit être supérieur au "
                "nombre d'actes déjà pris en charge")
        self.act_number = value
        self.save()

    def is_extended(self):
        if self.prolongation > 0:
            return True
        return False

    def add_prolongation(self, value=None):
        if not value:
            value = DEFAULT_ACT_NUMBER_PROLONGATION
        if self.is_extended():
            raise Exception(u'Prise en charge déja prolongée')
        self.prolongation = value
        self.save()

    def save(self, **kwargs):
        self.start_date = \
            datetime(self.start_date.year, self.start_date.month,
                self.start_date.day)
        self.end_date = self.start_date + \
            relativedelta(years=VALIDITY_PERIOD_TREATMENT_HEALTHCARE_YEARS) + \
            relativedelta(months=VALIDITY_PERIOD_TREATMENT_HEALTHCARE_MONTHS) + \
            relativedelta(days=VALIDITY_PERIOD_TREATMENT_HEALTHCARE_DAYS)
        super(CmppHealthCareTreatment, self).save(**kwargs)


class SessadHealthCareNotification(HealthCare):

    class Meta:
        app_label = 'dossiers'

    end_date = models.DateField()

    def save(self, **kwargs):
        self.start_date = \
            datetime(self.start_date.year, self.start_date.month,
                self.start_date.day)
        self.end_date = \
            datetime(self.end_date.year, self.end_date.month,
                self.end_date.day)
        super(SessadHealthCareNotification, self).save(**kwargs)

reversion.register(CmppHealthCareDiagnostic, follow=['healthcare_ptr'])
reversion.register(CmppHealthCareTreatment, follow=['healthcare_ptr'])
reversion.register(SessadHealthCareNotification, follow=['healthcare_ptr'])

class Status(NamedAbstractModel):

    class Meta:
        app_label = 'dossiers'
        verbose_name = u"Statut d'un état"
        verbose_name_plural = u"Statuts d'un état"

    type = models.CharField(max_length=80)
    services = models.ManyToManyField('ressources.Service')


class FileState(models.Model):

    class Meta:
        app_label = 'dossiers'
        verbose_name = u'Etat du dossier patient'
        verbose_name_plural = u'Etats du dossier patient'

    patient = models.ForeignKey('dossiers.PatientRecord',
        verbose_name=u'Dossier patient')
    status = models.ForeignKey('dossiers.Status', verbose_name=u'Statut')
    created = models.DateTimeField(u'Création', auto_now_add=True)
    date_selected = models.DateTimeField()
    author = \
        models.ForeignKey(User,
        verbose_name=u'Auteur')
    comment = models.TextField(max_length=3000, blank=True, null=True)
    previous_state = models.ForeignKey('FileState',
        verbose_name=u'Etat précédent', blank=True, null=True)

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
        return self.status.name + ' ' + str(self.date_selected)

    def delete(self, *args, **kwargs):
        next_state = self.get_next_state()
        if next_state and self.previous_state:
            next_state.previous_state = self.previous_state
            next_state.save()
        if self.patient.last_state == self:
            self.patient.last_state = self.previous_state
            self.patient.save()
        super(FileState, self).delete(*args, **kwargs)

class PatientAddress(models.Model):

    display_name = models.CharField(max_length=276,
            verbose_name=u'Adresse complète', editable=False)
    phone = PhoneNumberField(verbose_name=u"Téléphone", blank=True, null=True)
    fax = PhoneNumberField(verbose_name=u"Fax", blank=True, null=True)
    place_of_life = models.BooleanField(verbose_name=u"Lieu de vie")
    number = models.CharField(max_length=12,
            verbose_name=u"Numéro", blank=True, null=True)
    street = models.CharField(max_length=100,
            verbose_name=u"Rue", blank=True, null=True)
    address_complement = models.CharField(max_length=100,
            blank=True, null=True,
            verbose_name=u"Complément d'adresse")
    zip_code = ZipCodeField(verbose_name=u"Code postal", blank=True, null=True)
    city = models.CharField(max_length=60,
            verbose_name=u"Ville", blank=True, null=True)
    comment = models.TextField(verbose_name=u"Commentaire",
            null=True, blank=True)

    def __unicode__(self):
        return self.display_name

    def save(self, **kwargs):
        self.display_name = "%s %s, %s %s" % (self.number, self.street,  self.zip_code, self.city)
        super(PatientAddress, self).save(**kwargs)


class PatientContact(People):
    class Meta:
        verbose_name = u'Contact patient'
        verbose_name_plural = u'Contacts patient'

    mobile = PhoneNumberField(verbose_name=u"Téléphone mobile", blank=True, null=True)
    # carte vitale
    social_security_id = models.CharField(max_length=13, verbose_name=u"NIR",
            null=True, blank=True)
    birthdate = models.DateField(verbose_name=u"Date de naissance",
            null=True, blank=True)
    twinning_rank = models.IntegerField(verbose_name=u"Rang (gémellité)",
            null=True, blank=True)
    thirdparty_payer = models.BooleanField(verbose_name=u'Tiers-payant',
            default=False)
    begin_rights = models.DateField(verbose_name=u"Début de droits",
            null=True, blank=True)
    end_rights = models.DateField(verbose_name=u"Fin de droits",
            null=True, blank=True)
    health_center = models.ForeignKey('ressources.HealthCenter',
            verbose_name=u"Centre d'assurance maladie",
            null=True, blank=True)

    addresses = models.ManyToManyField('PatientAddress', verbose_name=u"Adresses")
    contact_comment = models.TextField(verbose_name=u"Commentaire",
            null=True, blank=True)

    def get_control_key(self):
        if self.social_security_id:
            return (97 - (int(self.social_security_id) % 97))
        return None


class PatientRecordManager(models.Manager):
    def for_service(self, service):
        return self.filter(service=service)

class PatientRecord(ServiceLinkedAbstractModel, PatientContact):
    objects = PatientRecordManager()

    class Meta:
        verbose_name = u'Dossier'
        verbose_name_plural = u'Dossiers'

    created = models.DateTimeField(u'création', auto_now_add=True)
    creator = \
        models.ForeignKey(User,
        verbose_name=u'Créateur dossier patient',
        editable=True)
    policyholder = models.ForeignKey('PatientContact',
            null=True, blank=True,
            verbose_name="Assuré", related_name="+")
    contacts = models.ManyToManyField('PatientContact',
            related_name='contact_of')
    nationality = models.CharField(verbose_name=u"Nationalité",
            max_length=70, null=True, blank=True)
    paper_id = models.CharField(max_length=6,
            verbose_name=u"N° dossier papier",
            null=True, blank=True)
    last_state = models.ForeignKey(FileState, related_name='+',
            null=True, on_delete=models.SET_NULL)
    comment = models.TextField(verbose_name=u"Commentaire",
            null=True, blank=True, default=None)
    pause = models.BooleanField(verbose_name=u"Pause facturation",
            default=False)
    socialisation_durations = models.ManyToManyField('ressources.SocialisationDuration',
            related_name='socialisation_duration_of')
    mdph_requests = models.ManyToManyField('ressources.MDPHRequest',
            related_name='mdph_requests_of')
    mdph_responses = models.ManyToManyField('ressources.MDPHResponse',
            related_name='mdph_responses_of')

    # Physiology and health data
    size = models.IntegerField(verbose_name=u"Taille (cm)",
            null=True, blank=True, default=None)
    weight = models.IntegerField(verbose_name=u"Poids (kg)",
            null=True, blank=True, default=None)
    pregnancy_term = models.IntegerField(verbose_name=u"Terme en semaines",
            null=True, blank=True, default=None)
    cranium_perimeter = models.DecimalField(verbose_name=u"Périmètre cranien", max_digits=5, decimal_places=2,
            null=True, blank=True, default=None)
    chest_perimeter = models.DecimalField(verbose_name=u"Périmètre thoracique", max_digits=5, decimal_places=2,
            null=True, blank=True, default=None)
    apgar_score_one = models.IntegerField(verbose_name=u"Test d'Apgar 1",
            null=True, blank=True, default=None)
    apgar_score_two = models.IntegerField(verbose_name=u"Test d'Apgar 2",
            null=True, blank=True, default=None)
    mises_1 = models.ManyToManyField('ressources.CodeCFTMEA', related_name="mises1",
            verbose_name=u"Axe I : catégories cliniques",
            null=True, blank=True, default=None)
    mises_2 = models.ManyToManyField('ressources.CodeCFTMEA', related_name="mises2",
            verbose_name=u"Axe II : facteurs organiques",
            null=True, blank=True, default=None)
    mises_3 = models.ManyToManyField('ressources.CodeCFTMEA', related_name="mises3",
            verbose_name=u"Axe II : facteurs environementaux",
            null=True, blank=True, default=None)

    # Inscription motive
    analysemotive = models.ForeignKey('ressources.AnalyseMotive',
            verbose_name=u"Motif (analysé)",
            null=True, blank=True, default=None)
    familymotive = models.ForeignKey('ressources.FamilyMotive',
            verbose_name=u"Motif (famille)",
            null=True, blank=True, default=None)
    advicegiver = models.ForeignKey('ressources.AdviceGiver',
            verbose_name=u"Conseilleur",
            null=True, blank=True, default=None)

    # Family
    sibship_place = models.IntegerField(verbose_name=u"Place dans la fratrie",
            null=True, blank=True, default=None)
    nb_children_family = models.IntegerField(verbose_name=u"Nombre d'enfants dans la fratrie",
            null=True, blank=True, default=None)
    parental_authority = models.ForeignKey('ressources.ParentalAuthorityType',
            verbose_name=u"Autorité parentale",
            null=True, blank=True, default=None)
    family_situation = models.ForeignKey('ressources.FamilySituationType',
            verbose_name=u"Situation familiale",
            null=True, blank=True, default=None)
    child_custody = models.ForeignKey('ressources.ParentalCustodyType',
            verbose_name=u"Garde parentale",
            null=True, blank=True, default=None)

    # Transport
    transporttype = models.ForeignKey('ressources.TransportType',
            verbose_name=u"Type de transport",
            null=True, blank=True, default=None)
    transportcompany = models.ForeignKey('ressources.TransportCompany',
            verbose_name=u"Compagnie de transport",
            null=True, blank=True, default=None)

    # FollowUp
    coordinators = models.ManyToManyField('personnes.Worker',
            verbose_name=u"Coordinateurs",
            null=True, blank=True, default=None)
    externaldoctor = models.ForeignKey('personnes.ExternalDoctor',
            verbose_name=u"Médecin extérieur",
            null=True, blank=True, default=None)
    externalintervener = models.ForeignKey('personnes.ExternalIntervener',
            verbose_name=u"Intervenant extérieur",
            null=True, blank=True, default=None)

    def __init__(self, *args, **kwargs):
        super(PatientRecord, self).__init__(*args, **kwargs)
        if not hasattr(self, 'service'):
            raise Exception('The field service is mandatory.')

    def get_state(self):
        return self.last_state

    def get_initial_state(self):
        return self.filestate_set.order_by('date_selected')[0]

    def get_current_state(self):
        today = date.today()
        return self.get_state_at_day(today)

    def get_state_at_day(self, date):
        state = self.get_state()
        while(state):
            if datetime(state.date_selected.year,
                    state.date_selected.month, state.date_selected.day) <= \
                    datetime(date.year, date.month, date.day):
                return state
            state = state.previous_state
        return self.get_state()

    def was_in_state_at_day(self, date, status_type):
        state_at_day = self.get_state_at_day(date)
        if state_at_day and state_at_day.status.type == status_type:
            return True
        return False

    def get_states_history(self):
        return self.filestate_set.order_by('date_selected')

    def can_be_deleted(self):
        for act in self.act_set.all():
            if act.is_state('VALIDE'):
                return False
        return True

    def delete(self, *args, **kwargs):
        if self.can_be_deleted():
            super(PatientRecord, self).delete(*args, **kwargs)

    def get_ondisk_directory(self, service):
        if not settings.PATIENT_FILES_BASE_DIRECTORY:
            return None

        dirnames = []
        dirname = self.last_name.upper()
        dirnames.append(dirname)
        if self.first_name:
            dirname = '%s %s' % (dirname, self.first_name)
            dirnames.append(dirname)
        if self.paper_id:
            dirname = '%s %s' % (dirname, self.paper_id)
            dirnames.append(dirname)

        for i, dirname in enumerate(dirnames):
            fullpath = os.path.join(settings.PATIENT_FILES_BASE_DIRECTORY, service, dirname)
            try:
                next_fullpath = os.path.join(settings.PATIENT_FILES_BASE_DIRECTORY, service, dirnames[i+1])
            except IndexError:
                pass
            else:
                 if os.path.exists(fullpath) and not os.path.exists(next_fullpath):
                     os.rename(fullpath, next_fullpath)
                 continue
            if not os.path.exists(fullpath):
                os.makedirs(fullpath)
            for subdir in settings.PATIENT_SUBDIRECTORIES:
                subdir_fullpath = os.path.join(fullpath, subdir)
                if not os.path.exists(subdir_fullpath):
                    os.makedirs(subdir_fullpath)
        return fullpath

    def get_client_side_directory(self, service):
        directory = self.get_ondisk_directory(service)
        if not directory:
            return None
        if not settings.CLIENT_SIDE_PATIENT_FILES_BASE_DIRECTORY:
            return None
        return os.path.join(settings.CLIENT_SIDE_PATIENT_FILES_BASE_DIRECTORY,
                            directory[len(settings.PATIENT_FILES_BASE_DIRECTORY)+1:])

    def set_state(self, status, author, date_selected=None, comment=None):
        if not author:
            raise Exception('Missing author to set state')
        if not date_selected:
            date_selected = datetime.now()
        current_state = self.get_state()
        if not current_state:
            raise Exception('Invalid patient record. '
                'Missing current state.')
        if date_selected < current_state.date_selected:
            raise Exception('You cannot set a state starting the %s that '
                'is before the previous state starting at day %s.' % \
                (str(date_selected), str(current_state.date_selected)))
        filestate = FileState.objects.create(patient=self, status=status,
            date_selected=date_selected, author=author, comment=comment,
            previous_state=current_state)
        self.last_state = filestate
        self.save()

    def change_day_selected_of_state(self, state, new_date):
        if state.previous_state:
            if new_date < state.previous_state.date_selected:
                raise Exception('You cannot set a state starting the %s '
                    'before the previous state starting at day %s.' % \
                    (str(new_date), str(state.previous_state.date_selected)))
        next_state = state.get_next_state()
        if next_state:
            if new_date > next_state.date_selected:
                raise Exception('You cannot set a state starting the %s '
                    'after the following state starting at day %s.' % \
                    (str(new_date), str(next_state.date_selected)))
        state.date_selected = new_date
        state.save()

    def remove_state(self, state):
        if state.patient.id != self.id:
            raise Exception('The state given is not about this patient '
                'record but about %s' % state.patient)
        next_state = state.get_next_state()
        if not next_state:
            self.remove_last_state()
        else:
            next_state.previous_state = state.previous_state
            next_state.save()
            state.delete()

    def remove_last_state(self):
        try:
            self.get_state().delete()
        except:
            pass

    # START Specific to sessad healthcare
    def get_last_notification(self):
        return SessadHealthCareNotification.objects.filter(patient=self, ).\
            latest('end_date')

    def days_before_notification_expiration(self):
        today = datetime.today()
        notification = self.get_last_notification(self)
        if not notification:
            return 0
        if notification.end_date < today:
            return 0
        else:
            return notification.end_date - today
    # END Specific to sessad healthcare

    # START Specific to cmpp healthcare
    def create_diag_healthcare(self, modifier):
        """
            Gestion de l'inscription automatique.

            Si un premier acte est validé alors une prise en charge
            diagnostique est ajoutée. Cela fera basculer le dossier dans l'état
            en diagnostic.

            A voir si auto ou manuel :
            Si ce n'est pas le premier acte validé mais que l'acte précédement
            facturé a plus d'un an, on peut créer une prise en charge
            diagnostique. Même s'il y a une prise en charge de traitement
            expirée depuis moins d'un an donc renouvelable.

        """
        acts = self.act_set.order_by('date')
        hcds = CmppHealthCareDiagnostic.objects.filter(patient=self).order_by('-start_date')
        if not hcds:
            # Pas de prise en charge, on recherche l'acte facturable le plus
            # ancien, on crée une pc diag à la même date.
            for act in acts:
                if act.is_state('VALIDE') and act.is_billable():
                    CmppHealthCareDiagnostic(patient=self, author=modifier,
                        start_date=act.date).save()
                    break
        else:
            # On recherche l'acte facturable non facturé le plus ancien et
            # l'on regarde s'il a plus d'un an
            try:
                last_billed_act = self.act_set.filter(is_billed=True).\
                    latest('date')
                if last_billed_act:
                    for act in acts:
                        if act.is_state('VALIDE') and \
                                act.is_billable() and \
                                (act.date - last_billed_act.date).days >= 365:
                            return True
            except:
                pass
        return False

    def automated_switch_state(self, modifier):
        # Quel est le dernier acte facturable.
        acts = self.act_set.order_by('-date')
        # Si cet acte peut-être pris en charge en diagnostic c'est un acte de
        # diagnostic, sinon c'est un acte de traitement.
        last_state_services = self.last_state.status.\
                services.values_list('name', flat=True)
        cmpp = Service.objects.get(name='CMPP')
        for act in acts:
            if act.is_state('VALIDE') and act.is_billable() and \
                    act.date >= self.get_state().date_selected and \
                    are_all_acts_of_the_day_locked(act.date):
                cared, hc = act.is_act_covered_by_diagnostic_healthcare()
                if hc:
                    if (self.last_state.status.type == "ACCUEIL" \
                            or self.last_state.status.type == "TRAITEMENT") \
                            and "CMPP" in last_state_services:
                        status = Status.objects.filter(type="DIAGNOSTIC").\
                                filter(services__name='CMPP')[0]
                        try:
                            self.set_state(status, modifier,
                                date_selected=act.date)
                        except:
                            pass
                # Sinon, si le dossier est en diag, s'il ne peut être couvert
                # en diag, il est en traitement.
                elif self.last_state.status.type == "DIAGNOSTIC" and \
                        "CMPP" in last_state_services:
                    status = Status.objects.filter(type="TRAITEMENT").\
                            filter(services__name='CMPP')[0]
                    try:
                        self.set_state(status, modifier,
                                date_selected=act.date)
                    except:
                        pass
                break
    # END Specific to cmpp healthcare

reversion.register(PatientRecord, follow=['people_ptr'])


def create_patient(first_name, last_name, service, creator,
        date_selected=None):
    logger.debug('create_patient: creation for patient %s %s in service %s '
        'by %s' % (first_name, last_name, service, creator))
    if not (first_name and last_name and service and creator):
        raise Exception('Missing parameter to create a patient record.')
    status = Status.objects.filter(type="ACCUEIL").filter(services=service)
    if not status:
        raise Exception('%s has no ACCEUIL status' % service.name)
    patient = PatientRecord.objects.create(first_name=first_name,
            last_name=last_name, service=service,
            creator=creator)
    fs = FileState(status=status[0], author=creator, previous_state=None)
    if not date_selected:
        date_selected = patient.created
    fs.patient = patient
    fs.date_selected = date_selected
    fs.save()
    patient.last_state = fs
    patient.save()
    return patient
