# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from calebasse.agenda.models import Event, EventType
from calebasse.agenda.managers import EventManager

from validation_states import VALIDATION_STATES


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

    def __unicode__(self):
        return self.state_name + ' ' + str(self.created)


class Act(models.Model):
    patient = models.ForeignKey('dossiers.PatientRecord')
    date = models.DateTimeField()
    act_type = models.ForeignKey('ressources.ActType',
            verbose_name=u'Type d\'acte')
    validation_locked = models.BooleanField(default=False,
            verbose_name=u'Vérouillage')
    is_billed = models.BooleanField(default=False,
            verbose_name=u'Facturé')
    switch_billable = models.BooleanField(default=False,
            verbose_name=u'Inverser type facturable')
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
            verbose_name=u'Thérapeutes')
    histories = models.ManyToManyField('HistoryAct')

    def is_absent(self):
        if self.get_state() in ('ABS_NON_EXC', 'ABS_EXC', 'ANNUL_NOUS',
                'ANNUL_FAMILLE', 'ABS_ESS_PPS', 'ENF_HOSP'):
            return True

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
        notifications = \
            SessadHealthCareNotification.objects.filter(patient=self.patient,
            start_date__lte=self.date, end_date__gte=self.date)
        if notifications:
            return True
    # END Specific to sessad healthcare

    def __unicode__(self):
        return '{0} le {1} pour {2} avec {3}'.format(
                self.act_type, self.date, self.patient,
                ', '.join(map(unicode, self.doctors.all())))

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, unicode(self), self.id)

    class Meta:
        verbose_name = u"Acte"
        verbose_name_plural = u"Actes"
        ordering = ['-date', 'patient']


class HistoryAct(models.Model):
    EVENT_CHOICES = (
            ('NR', u'Nouveau rendez-vous'),
            ('AV', u'Acte validé'),
            ('CF', u'En cours de facturation'),
            ('AF', u'Acte facturé'),
            )
    date = models.DateTimeField()
    event_type = models.CharField(max_length=2,
            choices=EVENT_CHOICES)
    description = models.TextField(default='')


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

        history = HistoryAct.objects.create(
                date = datetime.now(),
                event_type = 'NR')
        act_event = EventAct.objects.create(
                title=title,
                event_type=event_type,
                patient=patient,
                act_type=act_type,
                date=start_datetime,
                histories = [history]
                )
        act_event.doctors = participants
        ActValidationState(act=act_event, state_name='NON_VALIDE',
            author=creator, previous_state=None).save()

        return self._set_event(act_event, participants, description,
                services=[service], start_datetime=start_datetime,
                end_datetime=end_datetime,
                room=room, note=note, **rrule_params)


class EventAct(Act, Event):
    objects = EventActManager()

    VALIDATION_CODE_CHOICES = (
            ('absent', u'Absent'),
            ('present', u'Présent'),
            )
    attendance = models.CharField(max_length=16,
            choices=VALIDATION_CODE_CHOICES,
            default='absent',
            verbose_name=u'Présence')
    convocation_sent = models.BooleanField(blank=True,
            verbose_name=u'Convoqué')

    def __unicode__(self):
        return 'Rdv le {0} de {1} avec {2} pour {3}'.format(
                self.occurrence_set.all()[0].start_time, self.patient,
                ', '.join(map(unicode, self.participants.all())),
                self.act_type)

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, unicode(self),
            self.id)

    class Meta:
        verbose_name = 'Rendez-vous patient'
        verbose_name_plural = 'Rendez-vous patient'
        ordering = ['-date', 'patient']
