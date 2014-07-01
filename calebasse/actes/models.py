# -*- coding: utf-8 -*-
from datetime import date, time

from django.db import models
from django.contrib.auth.models import User

from calebasse.actes.validation_states import VALIDATION_STATES
from calebasse.ressources.models import ServiceLinkedAbstractModel
from ..middleware.request import get_request


class ActValidationState(models.Model):

    class Meta:
        app_label = 'actes'
        ordering = ('-created',)

    act = models.ForeignKey('actes.Act',
        verbose_name=u'Acte', editable=False)
    state_name = models.CharField(max_length=150)
    created = models.DateTimeField(u'Création', auto_now_add=True)
    author = \
        models.ForeignKey(User,
        verbose_name=u'Auteur', editable=False, blank=True, null=True,
        on_delete=models.SET_NULL)
    previous_state = models.ForeignKey('ActValidationState',
        verbose_name=u'Etat précédent',
        editable=False, blank=True, null=True)
    # To record if the validation has be done by the automated validation
    auto = models.BooleanField(default=False,
            verbose_name=u'Validaté automatiquement')

    def __repr__(self):
        return self.state_name + ' ' + str(self.created)

    def __unicode__(self):
        return VALIDATION_STATES[self.state_name]


class ActManager(models.Manager):
    def for_today(self, today=None):
        today = today or date.today()
        return self.filter(date=today)

    def create_act(self, author=None, **kwargs):
        act = Act(**kwargs)
        last_validation_state = ActValidationState.objects.create(
                act=act,state_name='NON_VALIDE',
                author=author, previous_state=None)
        act.last_validation_state = last_validation_state
        act.save()
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
    date = models.DateField(u'Date', db_index=True)
    time = models.TimeField(u'Heure', blank=True, null=True, default=time(), db_index=True)
    _duration = models.IntegerField(u'Durée en minutes', blank=True, null=True, default=0)
    act_type = models.ForeignKey('ressources.ActType',
            verbose_name=u'Type d\'acte')
    validation_locked = models.BooleanField(default=False,
            verbose_name=u'Vérouillage', db_index=True)
    is_billed = models.BooleanField(default=False,
            verbose_name=u'Facturé', db_index=True)
    is_lost = models.BooleanField(default=False,
            verbose_name=u'Acte perdu', db_index=True)
    last_validation_state = models.ForeignKey(ActValidationState,
            related_name='+',
            null=True, default=None,
            on_delete=models.SET_NULL)
    valide = models.BooleanField(default=False,
            verbose_name=u'Validé', db_index=True)
    switch_billable = models.BooleanField(default=False,
            verbose_name=u'Inverser type facturable')
    healthcare = models.ForeignKey('dossiers.HealthCare',
            blank=True,
            null=True,
            on_delete=models.SET_NULL,
            verbose_name=u'Prise en charge utilisée pour facturer (CMPP)')
    transport_company = models.ForeignKey('ressources.TransportCompany',
            blank=True,
            null=True,
            on_delete=models.SET_NULL,
            verbose_name=u'Compagnie de transport')
    transport_type = models.ForeignKey('ressources.TransportType',
            blank=True,
            null=True,
            on_delete=models.SET_NULL,
            verbose_name=u'Type de transport')
    doctors = models.ManyToManyField('personnes.Worker',
            limit_choices_to={'type__intervene': True},
            verbose_name=u'Intervenants')
    pause = models.BooleanField(default=False,
            verbose_name=u'Pause facturation', db_index=True)
    parent_event = models.ForeignKey('agenda.Event',
            verbose_name=u'Rendez-vous lié',
            blank=True, null=True,
            on_delete=models.SET_NULL)
    VALIDATION_CODE_CHOICES = (
            ('absent', u'Absent'),
            ('present', u'Présent'),
            )
    attendance = models.CharField(max_length=16,
            choices=VALIDATION_CODE_CHOICES,
            default='absent',
            verbose_name=u'Présence')
    comment = models.TextField(u'Commentaire', blank=True, null=True)
    old_id = models.CharField(max_length=256,
            verbose_name=u'Ancien ID', blank=True, null=True)

    @property
    def event(self):
        if self.parent_event:
            return self.parent_event.today_occurrence(self.date)
        return None

    @property
    def start_datetime(self):
        event = self.event
        if event:
            return event.start_datetime
        return self.date

    def get_hc_tag(self):
        if self.healthcare:
            beg = None
            try:
                self.healthcare.cmpphealthcaretreatment
                beg = 'T'
            except:
                pass
            try:
                self.healthcare.cmpphealthcarediagnostic
                beg = 'D'
            except:
                pass
            if beg:
                acts = list(self.healthcare.act_set.order_by('date').values_list('id', flat=True))
                beg += str(acts.index(self.id) + 1)
                return beg
        return None

    def is_new(self):
        return (not self.get_state() or self.is_state('NON_VALIDE'))

    def is_absent(self):
        state = self.get_state()
        if state and state.state_name in ('ABS_NON_EXC', 'ABS_EXC', 'ABS_INTER', 'ANNUL_NOUS',
                'ANNUL_FAMILLE', 'REPORTE', 'ABS_ESS_PPS', 'ENF_HOSP'):
            return True
        return False

    def is_present(self):
        return (not self.is_new() and not self.is_absent())

    def get_state(self):
        try:
            return self.last_validation_state
        except:
            return None

    def is_state(self, state_name):
        state = self.get_state()
        if state and state.state_name == state_name:
            return True
        return False

    def set_state(self, state_name, author, auto=False,
            change_state_check=True):
        if not self.id:
            self.save()
        if self.is_billed:
            raise Exception('Billed act state can not be modified')
        if not author:
            raise Exception('Missing author to set state')
        if not state_name in VALIDATION_STATES.keys():
            raise Exception("Etat d'acte non existant %s")
        current_state = self.get_state()
        last_validation_state = ActValidationState.objects.create(
                act=self,
                state_name=state_name,
                author=author,
                previous_state=current_state)
        self.last_validation_state = last_validation_state
        if state_name == 'VALIDE':
            self.valide = True
        else:
            self.valide = False
        self.save()

    def is_billable(self):
        billable = self.act_type.billable
        if (billable and not self.switch_billable) or \
                (not billable and self.switch_billable):
            return True
        return False

    # START Specific to sessad healthcare
    def was_covered_by_notification(self):
        from calebasse.dossiers.models import SessadHealthCareNotification
        notifications = \
            SessadHealthCareNotification.objects.filter(patient=self.patient,
            start_date__lte=self.date, end_date__gte=self.date)
        if notifications:
            return True
    # END Specific to sessad healthcare

    def save(self, *args, **kwargs):
        if self.parent_event and not self.parent_event.canceled:
            super(Act, self).save(*args, **kwargs)

    def duration(self):
        '''Return a displayable duration for this field.'''
        hours, remainder = divmod(self._duration, 60)
        return '%02d:%02d' % (hours, remainder)

    def __unicode__(self):
        if self.time:
            return u'{0} le {1} à {2} pour {3} avec {4}'.format(
                    self.act_type, self.date.strftime('%d/%m/%Y'),
                    self.time.strftime('%H:%M'), self.patient,
                    ', '.join(map(unicode, self.doctors.all())))
        return u'{0} le {1} pour {2} avec {3}'.format(
                self.act_type, self.date.strftime('%d/%m/%Y'), self.patient,
                ', '.join(map(unicode, self.doctors.all())))

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, unicode(self), self.id)

    def cancel(self):
        '''Parent event is canceled completely, or partially, act upon it.
        '''
        new_act = self.actvalidationstate_set.count() > 1
        if self.date <= date.today():
            if new_act:
                self.set_state('ANNUL_NOUS', get_request().user)
            self.parent_event = None
            self.save()
        else:
            self.delete()

    def get_invoice_number(self):
        try:
            if self.is_billed:
                return self.invoice_set.order_by('-number')[0].number
        except:
            pass
        return None

    class Meta:
        verbose_name = u"Acte"
        verbose_name_plural = u"Actes"
        ordering = ['-date', 'patient']


class ValidationMessage(ServiceLinkedAbstractModel):
    validation_date = models.DateTimeField()
    what = models.CharField(max_length=256)
    who = models.ForeignKey(User)
    when = models.DateTimeField(auto_now_add=True)
