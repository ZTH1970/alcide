# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from copy import copy

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from django import forms

from alcide.agenda import managers
from alcide.utils import weeks_since_epoch, weekday_ranks
from alcide.personnes.models import Holiday

from ..middleware.request import get_request

from interval import Interval

__all__ = (
    'EventType',
    'Event',
    'EventWithAct',
)

class EventType(models.Model):
    '''
    Simple ``Event`` classifcation.
    '''
    class Meta:
        verbose_name = u'Type d\'événement'
        verbose_name_plural = u'Types d\'événement'

    def __unicode__(self):
        return self.label

    label = models.CharField(_('label'), max_length=50)
    rank = models.IntegerField(_('Sorting Rank'), null=True, blank=True, default=0)

class Event(models.Model):
    '''
    Container model for general agenda events
    '''
    objects = managers.EventManager()

    title = models.CharField(_('Title'), max_length=60, blank=True, default="")
    description = models.TextField(_('Description'), max_length=100, blank=True, null=True)
    event_type = models.ForeignKey(EventType, verbose_name=u"Type d'événement")
    creator = models.ForeignKey(User, verbose_name=_(u'Créateur'), blank=True, null=True)
    create_date = models.DateTimeField(_(u'Date de création'), auto_now_add=True)

    services = models.ManyToManyField('ressources.Service',
            null=True, blank=True, default=None)
    participants = models.ManyToManyField('personnes.People',
            null=True, blank=True, default=None)
    ressource = models.ForeignKey('ressources.Ressource', blank=True, null=True,
                                  verbose_name=u'Ressource')

    start_datetime = models.DateTimeField(_(u'Début'), db_index=True)
    end_datetime = models.DateTimeField(_(u'Fin'), blank=True, null=True)
    old_ev_id = models.CharField(max_length=8, blank=True, null=True)
    old_rr_id = models.CharField(max_length=8, blank=True, null=True)
    # only used when there is no rr id
    old_rs_id = models.CharField(max_length=8, blank=True, null=True)
    # exception to is mutually exclusive with recurrence_periodicity
    # an exception cannot be periodic
    exception_to = models.ForeignKey('self', related_name='exceptions',
            blank=True, null=True,
            verbose_name=u'Exception à')
    exception_date = models.DateField(blank=True, null=True,
            verbose_name=u'Reporté du', db_index=True)
    # canceled can only be used with exception to
    canceled = models.BooleanField(_(u'Annulé'), db_index=True, default=False)

    PERIODS = (
            (1, u'Toutes les semaines'),
            (2, u'Une semaine sur deux'),
            (3, u'Une semaine sur trois'),
            (4, u'Une semaine sur quatre'),
            (5, u'Une semaine sur cinq')
    )
    OFFSET = range(0, 4)
    PERIODICITIES = (
            (1, u'Toutes les semaines'),
            (2, u'Une semaine sur deux'),
            (3, u'Une semaine sur trois'),
            (4, u'Une semaine sur quatre'),
            (5, u'Une semaine sur cinq'),
            (6, u'La première semaine du mois'),
            (7, u'La deuxième semaine du mois'),
            (8, u'La troisième semaine du mois'),
            (9, u'La quatrième semaine du mois'),
            (13, u'La cinquième semaine du mois'),
            (10, u'La dernière semaine du mois'),
            (11, u'Les semaines paires'),
            (12, u'Les semaines impaires')
    )
    WEEK_RANKS = (
            (0, u'La première semaine du mois'),
            (1, u'La deuxième semaine du mois'),
            (2, u'La troisième semaine du mois'),
            (3, u'La quatrième semaine du mois'),
            (4, u'La cinquième semaine du mois'),
            (-1, u'La dernière semaine du mois'),
#            (-2, u'L\'avant dernière semaine du mois'),
#            (-3, u'L\'antépénultième semaine du mois'),
#            (-4, u'L\'anté-antépénultième semaine du mois'),
#            (-5, u'L\'anté-anté-antépénultième semaine du mois')

    )
    PARITIES = (
            (0, u'Les semaines paires'),
            (1, u'Les semaines impaires')
    )
    recurrence_periodicity = models.PositiveIntegerField(
            choices=PERIODICITIES,
            verbose_name=u"Périodicité",
            default=None,
            blank=True,
            null=True,
            db_index=True)
    recurrence_week_day = models.PositiveIntegerField(default=0, db_index=True)
    recurrence_week_offset = models.PositiveIntegerField(
            choices=zip(OFFSET, OFFSET),
            verbose_name=u"Décalage en semaines par rapport au 1/1/1970 pour le calcul de période",
            default=0,
            db_index=True)
    recurrence_week_period = models.PositiveIntegerField(
            choices=PERIODS,
            verbose_name=u"Période en semaines",
            default=None,
            blank=True,
            null=True,
            db_index=True)
    recurrence_week_rank = models.IntegerField(
            verbose_name=u"Rang de la semaine dans le mois",
            choices=WEEK_RANKS,
            blank=True, null=True, db_index=True)
    recurrence_week_parity = models.PositiveIntegerField(
            choices=PARITIES,
            verbose_name=u"Parité des semaines",
            blank=True,
            null=True,
            db_index=True)
    recurrence_end_date = models.DateField(
            verbose_name=_(u'Fin de la récurrence'),
            blank=True, null=True,
            db_index=True)

    PERIOD_LIST_TO_FIELDS = [(1, None, None),
        (2, None, None),
        (3, None, None),
        (4, None, None),
        (5, None, None),
        (None, 0, None),
        (None, 1, None),
        (None, 2, None),
        (None, 3, None),
        (None, -1, None),
        (None, None, 0),
        (None, None, 1),
        (None, 4, None),
    ]

    class Meta:
        verbose_name = u'Evénement'
        verbose_name_plural = u'Evénements'
        ordering = ('start_datetime', 'end_datetime', 'title')
        unique_together = (('exception_to', 'exception_date'),)

    def __init__(self, *args, **kwargs):
        if kwargs.get('start_datetime') and not kwargs.has_key('recurrence_end_date'):
            kwargs['recurrence_end_date'] = kwargs.get('start_datetime').date()
        super(Event, self).__init__(*args, **kwargs)

    def clean(self):
        '''Initialize recurrence fields if they are not.'''
        self.sanitize()
        if self.recurrence_periodicity:
            if self.recurrence_end_date and self.start_datetime and self.recurrence_end_date < self.start_datetime.date():
                raise forms.ValidationError(u'La date de fin de périodicité doit être postérieure à la date de début.')
        if self.recurrence_week_parity is not None:
            if self.start_datetime:
                week = self.start_datetime.date().isocalendar()[1]
                start_week_parity = week % 2
                if start_week_parity != self.recurrence_week_parity:
                    raise forms.ValidationError(u'La date de départ de la périodicité est en semaine {week}.'.format(week=week))
        if self.recurrence_week_rank is not None and self.start_datetime:
            start_week_ranks = weekday_ranks(self.start_datetime.date())
            if self.recurrence_week_rank not in start_week_ranks:
                raise forms.ValidationError('La date de début de périodicité doit faire partie de la bonne semaine dans le mois.')

    def sanitize(self):
        if self.recurrence_periodicity:
            l = self.PERIOD_LIST_TO_FIELDS[self.recurrence_periodicity-1]
        else:
            l = None, None, None
        self.recurrence_week_period = l[0]
        self.recurrence_week_rank = l[1]
        self.recurrence_week_parity = l[2]
        if self.start_datetime:
            if self.recurrence_periodicity:
                self.recurrence_week_day = self.start_datetime.weekday()
            if self.recurrence_week_period is not None:
                self.recurrence_week_offset = weeks_since_epoch(self.start_datetime) % self.recurrence_week_period

    def timedelta(self):
        '''Distance between start and end of the event'''
        return self.end_datetime - self.start_datetime

    @property
    def time(self):
        return self.start_datetime.time()

    @property
    def date(self):
        return self.start_datetime.date()

    @property
    def duration(self):
        if self.timedelta():
            return self.timedelta().seconds / 60
        return 0

    def match_date(self, date):
        if self.is_recurring():
            # consider exceptions
            exception = self.get_exceptions_dict().get(date)
            if exception is not None:
                return exception if exception.match_date(date) else None
            if self.canceled:
                return None
            if date.weekday() != self.recurrence_week_day:
                return None
            if self.start_datetime.date() > date:
                return None
            if self.recurrence_end_date and self.recurrence_end_date < date:
                return None
            if self.recurrence_week_period is not None:
                if weeks_since_epoch(date) % self.recurrence_week_period != self.recurrence_week_offset:
                    return None
            elif self.recurrence_week_parity is not None:
                if date.isocalendar()[1] % 2 != self.recurrence_week_parity:
                    return None
            elif self.recurrence_week_rank is not None:
                if self.recurrence_week_rank not in weekday_ranks(date):
                    return None
            else:
                raise NotImplemented
            return self
        else:
            return self if date == self.start_datetime.date() else None


    def today_occurrence(self, today=None, match=False, upgrade=True):
        '''For a recurring event compute the today 'Event'.

           The computed event is the fake one that you cannot save to the database.
        '''
        today = today or date.today()
        if self.canceled:
            return None
        if match:
            exception = self.get_exceptions_dict().get(today)
            if exception:
                if exception.start_datetime.date() == today:
                    return exception.today_occurrence(today)
                else:
                    return None
        else:
            exception_or_self = self.match_date(today)
            if exception_or_self is None:
                return None
            if exception_or_self != self:
                return exception_or_self.today_occurrence(today)
        if self.event_type_id == 1 and type(self) != EventWithAct and upgrade:
           self = self.eventwithact
        if self.recurrence_periodicity is None:
            return self
        start_datetime = datetime.combine(today, self.start_datetime.timetz())
        end_datetime = start_datetime + self.timedelta()
        event = copy(self)
        event.exception_to = self
        event.exception_date = today
        event.start_datetime = start_datetime
        event.end_datetime = end_datetime
        event.recurrence_periodicity = None
        event.recurrence_week_offset = 0
        event.recurrence_week_period = None
        event.recurrence_week_parity = None
        event.recurrence_week_rank = None
        event.recurrence_end_date = None
        event.parent = self
        # the returned event is "virtual", it must not be saved
        old_save = event.save
        old_participants = list(self.participants.all())
        old_services = list(self.services.all())
        def save(*args, **kwargs):
            event.id = None
            event.event_ptr_id = None
            old_save(*args, **kwargs)
            if hasattr(self, 'exceptions_dict'):
                self.exceptions_dict[event.start_datetime.date()] = event
            event.services = old_services
            event.participants = old_participants
            event.save = old_save
        event.save = save
        return event

    def next_occurence(self, today=None):
        '''Returns the next occurence after today.'''
        today = today or date.today()
        for occurence in self.all_occurences():
            if occurence.start_datetime.date() > today:
                return occurence

    def is_recurring(self):
        '''Is this event multiple ?'''
        return self.recurrence_periodicity is not None

    def get_exceptions_dict(self):
        if not hasattr(self, 'exceptions_dict'):
            self.exceptions_dict = dict()
            if self.exception_to_id is None:
                for exception in self.exceptions.all():
                    self.exceptions_dict[exception.exception_date] = exception
        return self.exceptions_dict

    def all_occurences(self, limit=90):
        '''Returns all occurences of this event as virtual Event objects

           limit - compute occurrences until limit days in the future

           Default is to limit to 90 days.
        '''
        if self.recurrence_periodicity is not None:
            day = self.start_datetime.date()
            max_end_date = max(date.today(), self.start_datetime.date()) + timedelta(days=limit)
            end_date = min(self.recurrence_end_date or max_end_date, max_end_date)
            occurrences = []
            if self.recurrence_week_period is not None:
                delta = timedelta(days=self.recurrence_week_period*7)
                while day <= end_date:
                    occurrence = self.today_occurrence(day, True)
                    if occurrence is not None:
                        occurrences.append(occurrence)
                    day += delta
            elif self.recurrence_week_parity is not None:
                delta = timedelta(days=7)
                while day <= end_date:
                    if day.isocalendar()[1] % 2 == self.recurrence_week_parity:
                        occurrence = self.today_occurrence(day, True)
                        if occurrence is not None:
                            occurrences.append(occurrence)
                    day += delta
            elif self.recurrence_week_rank is not None:
                delta = timedelta(days=7)
                while day <= end_date:
                    if self.recurrence_week_rank in weekday_ranks(day):
                        occurrence = self.today_occurrence(day, True)
                        if occurrence is not None:
                            occurrences.append(occurrence)
                    day += delta
            for exception in self.exceptions.all():
                if not exception.canceled:
                    if exception.exception_date != exception.start_datetime.date() or exception.exception_date > end_date:
                        occurrences.append(exception.eventwithact if exception.event_type_id == 1 else exception)
            return sorted(occurrences, key=lambda o: o.start_datetime)
        else:
            return [self]

    def save(self, *args, **kwargs):
        assert self.recurrence_periodicity is None or self.exception_to is None
        assert self.exception_to is None or self.exception_to.recurrence_periodicity is not None
        assert self.start_datetime is not None
        self.sanitize() # init periodicity fields
        super(Event, self).save(*args, **kwargs)
        self.events_cleaning()
        self.acts_cleaning()

    def delete(self, *args, **kwargs):
        if not self.one_act_already_billed():
            for exception in self.exceptions.all():
                exception.delete()
            self.canceled = True
            if hasattr(self, 'eventwithact'):
                # Needed
                self.eventwithact.canceled = True
            # save will clean acts
            self.save(*args, **kwargs)

    @property
    def acts(self):
        from ..actes.models import Act
        return Act.objects.filter(
                models.Q(parent_event=self) | \
                models.Q(parent_event__exception_to=self))

    def one_act_not_new(self):
        '''
            Return True if at least one act of the present event or an act
            of one of its exceptions is not new.
        '''
        return True if [a for a in self.acts if not a.is_new()] else False

    def last_act_not_new(self):
        '''
            Return True if at least one act of the present event or an act
            of one of its exceptions is not new.
        '''
        act = None
        for a in self.acts:
            if not a.is_new():
                if not act or a.date > act.date:
                    act = a
        return act

    def one_act_already_billed(self):
        '''
            Return True if at least one act of the present event or an act
            of one of its exceptions is already billed.
        '''
        return self.acts.filter(already_billed=True).exists()

    def one_act_is_billed(self):
        '''
            Return True if at least one act of the present event or an act
            of one of its exceptions is billed.
        '''
        return self.acts.filter(is_billed=True).exists()

    def events_cleaning(self):
        """
            Delete exceptions out of bounds if not with an associated act
            already billed.
        """
        events = None
        if self.recurrence_end_date:
            events = Event.objects.filter(
                models.Q(exception_to=self,
                    exception_date__lt=self.start_datetime.date()) | \
                models.Q(exception_to=self,
                    exception_date__gt=self.recurrence_end_date))
        else:
            events = Event.objects.filter(exception_to=self,
                    exception_date__lt=self.start_datetime.date())
        for event in events:
            if hasattr(event, 'eventwithact'):
                if not event.eventwithact.act.already_billed:
                    event.delete()
            else:
                event.delete()

    def acts_cleaning(self):
        # list of occurences may have changed
        from ..actes.models import Act
        if self.exception_to:
            # maybe a new exception, so look for parent acts with same date
            # as exception date
            acts = Act.objects.filter(models.Q(parent_event=self)
                    |models.Q(parent_event=self.exception_to,
                        date=self.exception_date))
        else:
            acts = Act.objects.filter(parent_event=self)
        acts = acts.prefetch_related('actvalidationstate_set')
        if acts:
            eventwithact = self.eventwithact
            for act in acts:
                occurrence = eventwithact.today_occurrence(act.date)
                if occurrence:
                    occurrence.update_act(act)
                else:
                    if not act.already_billed:
                        act.delete()

    def to_interval(self):
        return Interval(self.start_datetime, self.end_datetime)

    def is_event_absence(self):
        return False

    def get_inactive_participants(self):
        return self.participants.filter(worker__enabled=False)

    def get_missing_participants(self):
        missing_participants = []
        for participant in self.participants.all():
            holidays = None
            worker = participant.worker
            holidays = Holiday.objects.for_worker(worker) \
                  .for_timed_period(self.start_datetime.date(), self.start_datetime.time(), self.end_datetime.time())
            if holidays:
                missing_participants.append(participant)
        return missing_participants

    RECURRENCE_DESCRIPTION = [
            u'Tous les %s',      #(1, None, None),
            u'Un %s sur deux',   #(2, None, None),
            u'Un %s sur trois',  #(3, None, None),
            u'Un %s sur quatre', #(4, None, None),
            u'Un %s sur cinq',   #(5, None, None),
            u'Le premier %s du mois',   #(None, 0, None),
            u'Le deuxième %s du mois',  #(None, 1, None),
            u'Le troisième %s du mois', #(None, 2, None),
            u'Le quatrième %s du mois', #(None, 3, None),
            u'Le dernier %s du mois',   #(None, 4, None),
            u'Les %s les semaines paires',    #(None, None, 0),
            u'Les %s les semaines impaires', #(None, None, 1)
    ]

    WEEKDAY_DESRIPTION = [
            u'lundi',
            u'mardi',
            u'mercredi',
            u'jeudi',
            u'vendredi',
            u'samedi',
            u'dimanche'
    ]

    def recurrence_description(self):
        '''Self description of this recurring event'''
        if not self.recurrence_periodicity:
            return None
        parts = []
        parts.append(self.RECURRENCE_DESCRIPTION[self.recurrence_periodicity-1] \
            % self.WEEKDAY_DESRIPTION[self.recurrence_week_day])
        if self.recurrence_end_date:
            parts.append(u'du')
        else:
            parts.append(u'à partir du')
        parts.append(self.start_datetime.strftime('%d/%m/%Y'))
        if self.recurrence_end_date:
            parts.append(u'au')
            parts.append(self.recurrence_end_date.strftime('%d/%m/%Y'))
        return u' '.join(parts)

    def is_absent(self):
        try:
            return self.eventwithact.is_absent()
        except self.DoesNotExist:
            return False

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Event: on {start_datetime} with {participants}'.format(
                start_datetime=self.start_datetime,
                participants=self.participants.all() if self.id else '<un-saved>')


class EventWithActManager(managers.EventManager):
    def create_patient_appointment(self, creator, title, patient,
            doctors=[], act_type=None, service=None, start_datetime=None, end_datetime=None,
            ressource=None, periodicity=1, until=False):
        appointment = self.create_event(creator=creator,
                title=title,
                event_type=EventType(id=1),
                participants=doctors,
                services=[service],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                ressource=ressource,
                periodicity=periodicity,
                until=until,
                act_type=act_type,
                patient=patient)
        return appointment


class EventWithAct(Event):
    '''An event corresponding to an act.'''
    objects = EventWithActManager()
    act_type = models.ForeignKey('ressources.ActType',
        verbose_name=u'Type d\'acte')
    patient = models.ForeignKey('dossiers.PatientRecord')
    convocation_sent = models.BooleanField(blank=True,
        verbose_name=u'Convoqué', db_index=True, default=False)


    @property
    def act(self):
        for act in self.act_set.all():
            if act.date == self.start_datetime.date():
                return act
        return self.build_act()

    def get_state(self):
        act = self.act
        if act.id:
            return act.get_state()
        return None

    def is_absent(self):
        act = self.act
        if act.id:
            return act.is_absent()
        return False

    def build_act(self):
        from ..actes.models import Act, ActValidationState
        act = Act()
        self.init_act(act)
        old_save = act.save
        def save(*args, **kwargs):
            act.save = old_save
            old_save(*args, **kwargs)
            act.doctors = (participant.worker for participant in self.participants.all())
            last_validation_state = ActValidationState.objects.create(
                    act=act, state_name='NON_VALIDE',
                    author=self.creator, previous_state=None)
            act.last_validation_state = last_validation_state
            old_save(*args, **kwargs)
        act.save = save
        return act

    def update_act(self, act):
        '''Update an act to match details of the meeting'''
        self.init_act(act)
        act.save()

    def init_act(self, act):
        if not act.is_billed:
            delta = self.timedelta()
            duration = delta.seconds // 60
            act._duration = duration
            act.act_type = self.act_type
            act.patient = self.patient
            act.date = self.start_datetime.date()
            act.time = self.start_datetime.time()
        act.parent_event = self

    def save(self, *args, **kwargs):
        '''Force event_type to be patient meeting.'''
        self.event_type = EventType(id=1)
        super(EventWithAct, self).save(*args, **kwargs)

    def is_event_absence(self):
        return self.act.is_absent()

    def __unicode__(self):
        kwargs = {
                'patient': self.patient,
                'start_datetime': self.start_datetime,
                'act_type': self.act_type
        }
        kwargs['doctors'] = ', '.join(map(unicode, self.participants.all())) if self.id else ''
        return u'Rdv le {start_datetime} de {patient} avec {doctors} pour ' \
            '{act_type} ({act_type.id})'.format(**kwargs)


from django.db.models.signals import m2m_changed
from django.dispatch import receiver


@receiver(m2m_changed, sender=Event.participants.through)
def participants_changed(sender, instance, action, **kwargs):
    if action.startswith('post'):
        workers = [ p.worker for p in instance.participants.prefetch_related('worker') ]
        for act in instance.act_set.all():
            act.doctors = workers
