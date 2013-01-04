# -*- coding: utf-8 -*-
from datetime import date

from django.db import models
from django.contrib.auth.models import User

import reversion

from calebasse.agenda.models import Event, EventType
from calebasse.agenda.managers import EventManager
from calebasse.ressources.models import ServiceLinkedAbstractModel

from validation_states import VALIDATION_STATES, NON_VALIDE


class ActValidationState(models.Model):

    class Meta:
        app_label = 'actes'

    act = models.ForeignKey('actes.Act',
        verbose_name=u'Acte', editable=False)
    state_name = models.CharField(max_length=150)
    created = models.DateTimeField(u'Création', auto_now_add=True)
    author = \
        models.ForeignKey(User,
        verbose_name=u'Auteur', editable=False)
    previous_state = models.ForeignKey('ActValidationState',
        verbose_name=u'Etat précédent',
        editable=False, blank=True, null=True)
    # To record if the validation has be done by the automated validation
    auto = models.BooleanField(default=False,
            verbose_name=u'Vérouillage')

    def __repr__(self):
        return self.state_name + ' ' + str(self.created)

    def __unicode__(self):
        return VALIDATION_STATES[self.state_name]


class ActManager(models.Manager):
    def create_act(self, author=None, **kwargs):
        act = self.create(**kwargs)
        ActValidationState.objects.create(act=act,state_name='NON_VALIDE',
            author=author, previous_state=None)
        return act

    def next_acts(self, patient_record, today=None):
        today = today or date.today()
        return self.filter(date__gte=today) \
                .filter(patient=patient_record) \
                .order_by('date')

    def last_acts(self, patient_record, today=None):
        today = today or date.today()
        return self.filter(date__lte=today) \
                .filter(patient=patient_record) \
                .order_by('-date')


class Act(models.Model):
    objects = ActManager()

    patient = models.ForeignKey('dossiers.PatientRecord')
    date = models.DateField()
    _duration = models.IntegerField(u'Durée en minutes', default=0)
    act_type = models.ForeignKey('ressources.ActType',
            verbose_name=u'Type d\'acte')
    validation_locked = models.BooleanField(default=False,
            verbose_name=u'Vérouillage')
    is_billed = models.BooleanField(default=False,
            verbose_name=u'Facturé')
    switch_billable = models.BooleanField(default=False,
            verbose_name=u'Inverser type facturable')
    healthcare = models.ForeignKey('dossiers.HealthCare',
            blank=True,
            null=True,
            verbose_name=u'Prise en charge utilisée pour facturer (CMPP)')
    transport_company = models.ForeignKey('ressources.TransportCompany',
            blank=True,
            null=True,
            verbose_name=u'Compagnie de transport')
    transport_type = models.ForeignKey('ressources.TransportType',
            blank=True,
            null=True,
            verbose_name=u'Type de transport')
    doctors = models.ManyToManyField('personnes.Worker',
            limit_choices_to={'type__intervene': True},
            verbose_name=u'Intervenants')
    pause = models.BooleanField(default=False,
            verbose_name=u'Pause facturation')
    parent_event = models.ForeignKey('agenda.Event',
            verbose_name=u'Rendez-vous lié',
            blank=True, null=True)
    VALIDATION_CODE_CHOICES = (
            ('absent', u'Absent'),
            ('present', u'Présent'),
            )
    attendance = models.CharField(max_length=16,
            choices=VALIDATION_CODE_CHOICES,
            default='absent',
            verbose_name=u'Présence')

    @property
    def event(self):
        if self.parent_event:
            return self.parent_event.today_occurence(self.date)
        return None

    @property
    def start_datetime(self):
        event = self.event
        if event:
            return event.start_datetime
        return self.date

    def get_hc_tag(self):
        if self.healthcare:
            try:
                self.healthcare.cmpphealthcaretreatment
                return 'T'
            except:
                pass
            try:
                self.healthcare.cmpphealthcarediagnostic
                acts = self.healthcare.act_set.order_by('date')
                i = 1
                for act in acts:
                    if act.id == self.id:
                        return 'D' + str(i)
                    i = i + 1
            except:
                pass
        return None

    def is_absent(self):
        state = self.get_state()
        if state and state.state_name in ('ABS_NON_EXC', 'ABS_EXC', 'ANNUL_NOUS',
                'ANNUL_FAMILLE', 'REPORTE', 'ABS_ESS_PPS', 'ENF_HOSP'):
            return True
        return False

    def get_state(self):
        return self.actvalidationstate_set.latest('created')

    def is_state(self, state_name):
        state = self.get_state()
        if state and state.state_name == state_name:
            return True
        return False

    def set_state(self, state_name, author, auto=False,
            change_state_check=True):
        if not author:
            raise Exception('Missing author to set state')
        if not state_name in VALIDATION_STATES.keys():
            raise Exception("Etat d'acte non existant %s")
        current_state = self.get_state()
        ActValidationState(act=self, state_name=state_name,
            author=author, previous_state=current_state).save()

    def is_billable(self):
        if (self.act_type.billable and not self.switch_billable) or \
                (not self.act_type.billable and self.switch_billable):
            return True

    # START Specific to sessad healthcare
    def was_covered_by_notification(self):
        from calebasse.dossiers.models import SessadHealthCareNotification
        notifications = \
            SessadHealthCareNotification.objects.filter(patient=self.patient,
            start_date__lte=self.date, end_date__gte=self.date)
        if notifications:
            return True
    # END Specific to sessad healthcare

    # START Specific to cmpp healthcare
    def is_act_covered_by_diagnostic_healthcare(self):
        from calebasse.dossiers.models import CmppHealthCareDiagnostic
        from validation import are_all_acts_of_the_day_locked
        # L'acte est déja pointé par une prise en charge
        if self.is_billed:
            # Sinon ce peut une refacturation, donc ne pas tenir compte qu'il
            # y est une healthcare non vide
            if self.healthcare and isinstance(self.healthcare,
                    CmppHealthCareDiagnostic):
                return (False, self.healthcare)
            elif self.healthcare:
                return (False, None)
        # L'acte doit être facturable
        if not (are_all_acts_of_the_day_locked(self.date) and \
                self.is_state('VALIDE') and self.is_billable()):
            return (False, None)
        # On prend la dernière prise en charge diagnostic, l'acte ne sera pas
        # pris en charge sur une prise en charge précédente
        # Il peut arriver que l'on ait ajouté une prise en charge de
        # traitement alors que tous les actes pour le diag ne sont pas encore facturés
        try:
            hc = CmppHealthCareDiagnostic.objects.\
                filter(patient=self.patient).latest('start_date')
        except:
            return (False, None)
        if not hc:
            # On pourrait ici créer une prise en charge de diagnostic
            return (False, None)
        if self.date < hc.start_date:
            return (False, None)
        # Les acts facturés déja couvert par la prise en charge sont pointés
        # dans hc.act_set.all()
        nb_acts_billed = len(hc.act_set.all())
        if nb_acts_billed >= hc.get_act_number():
            return (False, None)
        # Il faut ajouter les actes facturables non encore facturés qui précède cet
        # acte
        acts_billable = [a for a in self.patient.act_set.\
            filter(is_billed=False).order_by('date') \
            if are_all_acts_of_the_day_locked(a.date) and \
            a.is_state('VALIDE') and a.is_billable()]
        count = 0
        for a in acts_billable:
            if nb_acts_billed + count >= hc.get_act_number():
                return (False, None)
            if a.date >= hc.start_date:
                if a.id == self.id:
                    return (True, hc)
                count = count + 1
        return (False, None)

#    def is_act_covered_by_treatment_healthcare(self):
#        # L'acte est déja pointé par une prise en charge
#        if self.is_billed:
#            # Sinon ce peut une refacturation, donc ne pas tenir compte qu'il
#            # y est une healthcare non vide
#            if self.healthcare and isinstance(self.healthcare,
#                    CmppHealthCareTreatment):
#                return (False, self.healthcare)
#            elif self.healthcare:
#                return (False, None)
#        # L'acte doit être facturable
#        if not (are_all_acts_of_the_day_locked(self.date) and \
#                self.is_state('VALIDE') and self.is_billable()):
#            return (False, None)
#        # On prend la dernière prise en charge diagnostic, l'acte ne sera pas
#        # pris en charge sur une prise en charge précédente
#        # Il peut arriver que l'on ait ajouté une prise en charge de
#        # traitement alors que tous les actes pour le diag ne sont pas encore facturés
#        try:
#            hc = CmppHealthCareTreatment.objects.\
#                filter(patient=self.patient).latest('start_date')
#        except:
#            return (False, None)
#        if not hc:
#            return (False, None)
#        if self.date < hc.start_date or self.date > hc.end_date:
#            return (False, None)
#        # Les acts facturés déja couvert par la prise en charge sont pointés
#        # dans hc.act_set.all()
#        nb_acts_billed = len(hc.act_set.all())
#        if nb_acts_billed >= hc.get_act_number():
#            return (False, None)
#        # Il faut ajouter les actes facturables non encore facturés qui précède cet
#        # acte
#        acts_billable = [a for a in self.patient.act_set.\
#            filter(is_billed=False).order_by('date') \
#            if are_all_acts_of_the_day_locked(a.date) and \
#            a.is_state('VALIDE') and a.is_billable()]
#        count = 0
#        for a in acts_billable:
#            if nb_acts_billed + count >= hc.get_act_number():
#                return (False, None)
#            if a.date >= hc.start_date and a.date <= hc.end_date:
#                if a.id == self.id:
#                    return (True, hc)
#                count = count + 1
#        return (False, None)
# END Specific to cmpp healthcare

    def duration(self):
        '''Return a displayable duration for this field.'''
        hours, remainder = divmod(self._duration, 60)
        return '%02d:%02d' % (hours, remainder)

    def __unicode__(self):
        return u'{0} le {1} pour {2} avec {3}'.format(
                self.act_type, self.date, self.patient,
                ', '.join(map(unicode, self.doctors.all())))

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, unicode(self), self.id)

    class Meta:
        verbose_name = u"Acte"
        verbose_name_plural = u"Actes"
        ordering = ['-date', 'patient']


class EventActManager(EventManager):

    def create_patient_appointment(self, creator, title, patient, participants,
            act_type, service, start_datetime, end_datetime, description='',
            room=None, note=None, **rrule_params):
        """
        This method allow you to create a new patient appointment quickly

        Args:
            title: patient appointment title (str)
            patient: Patient object
            participants: List of CalebasseUser (therapists)
            act_type: ActType object
            service: Service object. Use session service by defaut
            start_datetime: datetime with the start date and time
            end_datetime: datetime with the end date and time
            freq, count, until, byweekday, rrule_params:
            follow the ``dateutils`` API (see http://labix.org/python-dateutil)

        Example:
            Look at calebasse.agenda.tests.EventTest (test_create_appointments
            method)
        """

        event_type, created = EventType.objects.get_or_create(
                label=u"Rendez-vous patient"
                )

        act_event = EventAct.objects.create(
                title=title,
                event_type=event_type,
                patient=patient,
                act_type=act_type,
                date=start_datetime,
                )
        act_event.doctors = participants
        ActValidationState(act=act_event, state_name='NON_VALIDE',
            author=creator, previous_state=None).save()

        return self._set_event(act_event, participants, description,
                services=[service], start_datetime=start_datetime,
                end_datetime=end_datetime,
                room=room, note=note, **rrule_params)


class ValidationMessage(ServiceLinkedAbstractModel):
    validation_date = models.DateTimeField()
    what = models.CharField(max_length=256)
    who = models.ForeignKey(User)
    when = models.DateTimeField(auto_now_add=True)
