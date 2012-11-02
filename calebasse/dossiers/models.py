# -*- coding: utf-8 -*-

import logging

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from calebasse.personnes.models import People
from calebasse.ressources.models import ServiceLinkedAbstractModel
from calebasse.dossiers.states import STATES, STATE_ACCUEIL

logger = logging.getLogger('calebasse.dossiers')


class FileState(models.Model):

    class Meta:
        app_label = 'dossiers'

    patient = models.ForeignKey('dossiers.PatientRecord',
        verbose_name=u'Dossier patient', editable=False)
    state_name = models.CharField(max_length=150)
    created = models.DateTimeField(u'Création', auto_now_add=True)
    date_selected = models.DateTimeField()
    author = \
        models.ForeignKey(User,
        verbose_name=u'Auteur', editable=False)
    comment = models.TextField(max_length=3000, blank=True, null=True)
    previous_state = models.ForeignKey('FileState',
        verbose_name=u'Etat précédent',
        editable=False, blank=True, null=True)

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
        return self.state_name + ' ' + str(self.date_selected)


class PatientRecord(ServiceLinkedAbstractModel, People):
    class Meta:
        verbose_name = u'Dossier'
        verbose_name_plural = u'Dossiers'

    created = models.DateTimeField(u'création', auto_now_add=True)
    creator = \
        models.ForeignKey(User,
        verbose_name=u'Créateur dossier patient',
        editable=False)
    contacts = models.ManyToManyField('personnes.People',
            related_name='contact_of')
    birthdate = models.DateField()
    paper_id = models.CharField(max_length=12,
            null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(PatientRecord, self).__init__(*args, **kwargs)
        if not hasattr(self, 'service'):
            raise Exception('The field service is mandatory.')

    def get_state(self):
        last_state = self.filestate_set.latest('date_selected')
        multiple = self.filestate_set.\
            filter(date_selected=last_state.date_selected)
        if len(multiple) > 1:
            last_state = multiple.latest('created')
        return last_state

    def get_state_at_day(self, date):
        state = self.get_state()
        while(state):
            if datetime(state.date_selected.year,
                    state.date_selected.month, state.date_selected.day) <= \
                    datetime(date.year, date.month, date.day):
                return state
            state = state.previous_state
        return None

    def was_in_state_at_day(self, date, state_name):
        state_at_day = self.get_state_at_day(date)
        if state_at_day and state_at_day.state_name == state_name:
            return True
        return False

    def get_states_history(self):
        return self.filestate_set.order_by('date_selected')

    def set_state(self, state_name, author, date_selected=None, comment=None):
        if not author:
            raise Exception('Missing author to set state')
        if not state_name in STATES[self.service.name].keys():
            raise Exception('Etat de dossier '
                'non existant dans le service %s.' % self.service.name)
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
        FileState(patient=self, state_name=state_name,
            date_selected=date_selected, author=author, comment=comment,
            previous_state=current_state).save()

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


def create_patient(first_name, last_name, service, creator,
        date_selected=None):
    logger.debug('create_patient: creation for patient %s %s in service %s '
        'by %s' % (first_name, last_name, service, creator))
    if not (first_name and last_name and service and creator):
        raise Exception('Missing parameter to create a patient record.')
    patient = PatientRecord(first_name=first_name, last_name=last_name,
        service=service, creator=creator)
    patient.save()
    if not date_selected:
        date_selected = patient.created
    FileState(patient=patient, state_name=STATE_ACCUEIL[service.name],
        date_selected=date_selected, author=creator,
        previous_state=None).save()
    return patient
