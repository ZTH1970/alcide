# -*- coding: utf-8 -*-

import logging

from datetime import datetime, date
from datetime import timedelta

from django import forms
from django.db import models
from django.contrib.auth.models import User

import reversion

from calebasse.models import PhoneNumberField, ZipCodeField
from calebasse.personnes.models import People
from calebasse.ressources.models import (ServiceLinkedAbstractModel,
        NamedAbstractModel, Service)
from calebasse.actes.validation import are_all_acts_of_the_day_locked

DEFAULT_ACT_NUMBER_DIAGNOSTIC = 6
DEFAULT_ACT_NUMBER_TREATMENT = 30
DEFAULT_ACT_NUMBER_PROLONGATION = 10
VALIDITY_PERIOD_TREATMENT_HEALTHCARE = 365

logger = logging.getLogger('calebasse.dossiers')


class HealthCare(models.Model):

    class Meta:
        app_label = 'dossiers'

    patient = models.ForeignKey('dossiers.PatientRecord',
        verbose_name=u'Dossier patient', editable=False)
    created = models.DateTimeField(u'Création', auto_now_add=True)
    author = \
        models.ForeignKey(User,
        verbose_name=u'Auteur', editable=False)
    comment = models.TextField(max_length=3000, blank=True, null=True)
    start_date = models.DateTimeField()


class CmppHealthCareDiagnostic(HealthCare):

    class Meta:
        app_label = 'dossiers'

    _act_number = models.IntegerField(default=DEFAULT_ACT_NUMBER_DIAGNOSTIC)

    def get_act_number(self):
        return self._act_number

    def save(self, **kwargs):
        self.start_date = \
            datetime(self.start_date.year, self.start_date.month,
                self.start_date.day)
        super(CmppHealthCareDiagnostic, self).save(**kwargs)


class CmppHealthCareTreatment(HealthCare):

    class Meta:
        app_label = 'dossiers'

    _act_number = models.IntegerField(default=DEFAULT_ACT_NUMBER_TREATMENT)
    end_date = models.DateTimeField()
    prolongation = models.IntegerField(default=0,
            verbose_name=u'Prolongation')

    def get_act_number(self):
        if self.is_extended():
            return self._act_number + self.prolongation
        return self._act_number

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
            timedelta(days=VALIDITY_PERIOD_TREATMENT_HEALTHCARE)

        super(CmppHealthCareTreatment, self).save(**kwargs)


class SessadHealthCareNotification(HealthCare):

    class Meta:
        app_label = 'dossiers'

    end_date = models.DateTimeField()

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
    status = models.ForeignKey('dossiers.Status')
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

class PatientAddress(models.Model):

    def __unicode__(self):
        return self.address + ', ' + self.city

    phone = PhoneNumberField(verbose_name=u"Téléphone", blank=True, null=True)
    fax = PhoneNumberField(verbose_name=u"Fax", blank=True, null=True)
    address = models.CharField(max_length=120,
            verbose_name=u"Adresse")
    address_complement = models.CharField(max_length=120,
            blank=True,
            null=True,
            default=None,
            verbose_name=u"Complément d'addresse")
    zip_code = ZipCodeField(verbose_name=u"Code postal")
    city = models.CharField(max_length=80,
            verbose_name=u"Ville")

class PatientContact(People):
    class Meta:
        verbose_name = u'Contact patient'
        verbose_name_plural = u'Contacts patient'

    mobile = PhoneNumberField(verbose_name=u"Téléphone mobile", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    social_security_id = models.CharField(max_length=13, verbose_name=u"Numéro de sécurité sociale")
    addresses = models.ManyToManyField('PatientAddress', verbose_name=u"Adresses",
            blank=True, null=True)


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
    contacts = models.ManyToManyField('personnes.People',
            related_name='contact_of')
    birthdate = models.DateField(verbose_name=u"Date de naissance",
            null=True, blank=True)
    nationality = models.CharField(verbose_name=u"Nationalité",
            max_length=70, null=True, blank=True)
    paper_id = models.CharField(max_length=12,
            null=True, blank=True)
    last_state = models.ForeignKey(FileState, related_name='+',
            null=True)
    school = models.ForeignKey('ressources.School',
            null=True, blank=True, default=None)
    comment = models.TextField(verbose_name=u"Commentaire",
            null=True, blank=True, default=None)
    pause = models.BooleanField(verbose_name=u"Pause facturation",
            default=False)

    # Physiology
    size = models.IntegerField(verbose_name=u"Taille (cm)",
            null=True, blank=True, default=None)
    weight = models.IntegerField(verbose_name=u"Poids (kg)",
            null=True, blank=True, default=None)
    pregnancy_term = models.IntegerField(verbose_name=u"Terme en semaines",
            null=True, blank=True, default=None)

    # Inscription motive
    analysemotive = models.ForeignKey('ressources.AnalyseMotive',
            verbose_name=u"Motif (analysé)",
            null=True, blank=True, default=None)
    famillymotive = models.ForeignKey('ressources.FamillyMotive',
            verbose_name=u"Motif (famille)",
            null=True, blank=True, default=None)
    advicegiver = models.ForeignKey('ressources.AdviceGiver',
            verbose_name=u"Conseilleur",
            null=True, blank=True, default=None)

    # Familly
    sibship_place = models.IntegerField(verbose_name=u"Place dans la fratrie",
            null=True, blank=True, default=None)
    nb_children_family = models.IntegerField(verbose_name=u"Nombre d'enfants dans la fratrie",
            null=True, blank=True, default=None)
    twinning_rank = models.IntegerField(verbose_name=u"Rang (gémellité)",
            null=True, blank=True, default=None)
    parental_authority = models.ForeignKey('ressources.ParentalAuthorityType',
            verbose_name=u"Autorité parentale",
            null=True, blank=True, default=None)
    familly_situation = models.ForeignKey('ressources.FamilySituationType',
            verbose_name=u"Situation familiale",
            null=True, blank=True, default=None)
    child_custody = models.ForeignKey('ressources.ParentalCustodyType',
            verbose_name=u"Garde parentale",
            null=True, blank=True, default=None)

    # Transport
    transport_type = models.ForeignKey('ressources.TransportType',
            verbose_name=u"Type de transport",
            null=True, blank=True, default=None)
    transport_company = models.ForeignKey('ressources.TransportCompany',
            verbose_name=u"Compagnie de transport",
            null=True, blank=True, default=None)

    def __init__(self, *args, **kwargs):
        super(PatientRecord, self).__init__(*args, **kwargs)
        if not hasattr(self, 'service'):
            raise Exception('The field service is mandatory.')

    def get_state(self):
        return self.last_state

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
        hcs = self.healthcare_set.order_by('-start_date')
        if not hcs:
            # Pas de prise en charge, on recherche l'acte facturable le plus
            # ancien, on crée une pc diag à la même date.
            for act in acts:
                if are_all_acts_of_the_day_locked(act.date) and \
                        act.is_state('VALIDE') and act.is_billable():
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
                        if are_all_acts_of_the_day_locked(act.date) and \
                                act.is_state('VALIDE') and \
                                act.is_billable() and \
                                (act.date - last_billed_act.date).days >= 365:
                            CmppHealthCareDiagnostic(patient=self,
                                author=modifier, start_date=act.date).save()
                            break
            except:
                pass

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
