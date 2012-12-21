# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil import rrule

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models

from calebasse.agenda import managers
from interval import Interval

__all__ = (
    'Note',
    'EventType',
    'Event',
    'Occurrence',
)

class Note(models.Model):
    '''
    A generic model for adding simple, arbitrary notes to other models such as
    ``Event`` or ``Occurrence``.
    '''

    class Meta:
        verbose_name = u'Note'
        verbose_name_plural = u'Notes'

    def __unicode__(self):
        return self.note

    note = models.TextField(_('note'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    content_type = models.ForeignKey(ContentType)


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
    Container model for general metadata and associated ``Occurrence`` entries.
    '''
    objects = managers.EventManager()

    title = models.CharField(_('Title'), max_length=32, blank=True)
    description = models.TextField(_('Description'), max_length=100)
    event_type = models.ForeignKey(EventType, verbose_name=u"Type d'événement")
    notes = generic.GenericRelation(Note, verbose_name=_('notes'))

    services = models.ManyToManyField('ressources.Service',
            null=True, blank=True, default=None)
    participants = models.ManyToManyField('personnes.People',
            null=True, blank=True, default=None)
    room = models.ForeignKey('ressources.Room', blank=True, null=True,
            verbose_name=u'Salle')

    class Meta:
        verbose_name = u'Evénement'
        verbose_name_plural = u'Evénements'
        ordering = ('title', )


    def __unicode__(self):
        return self.title

    def add_occurrences(self, start_time, end_time, room=None, **rrule_params):
        '''
        Add one or more occurences to the event using a comparable API to 
        ``dateutil.rrule``. 

        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        '''
        rrule_params.setdefault('freq', rrule.DAILY)

        if 'count' not in rrule_params and 'until' not in rrule_params:
            self.occurrence_set.create(start_time=start_time, end_time=end_time)
        else:
            delta = end_time - start_time
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                self.occurrence_set.create(start_time=ev, end_time=ev + delta)

    def upcoming_occurrences(self):
        '''
        Return all occurrences that are set to start on or after the current
        time.
        '''
        return self.occurrence_set.filter(start_time__gte=datetime.now())

    def next_occurrence(self):
        '''
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        '''
        upcoming = self.upcoming_occurrences()
        return upcoming and upcoming[0] or None

    def daily_occurrences(self, dt=None):
        '''
        Convenience method wrapping ``Occurrence.objects.daily_occurrences``.
        '''
        return Occurrence.objects.daily_occurrences(dt=dt, event=self)


class Occurrence(models.Model):
    '''
    Represents the start end time for a specific occurrence of a master ``Event``
    object.
    '''
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event = models.ForeignKey('Event', verbose_name=_('event'), editable=False)
    notes = models.ManyToManyField('Note', verbose_name=_('notes'),
            null=True, blank=True, default=None)

    objects = managers.OccurrenceManager()

    class Meta:
        verbose_name = u'Occurrence'
        verbose_name_plural = u'Occurrences'
        ordering = ('start_time', 'end_time')

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.start_time.isoformat())

    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)

    @property
    def title(self):
        return self.event.title

    @property
    def event_type(self):
        return self.event.event_type

    def to_interval(self):
        return Interval(self.start_time, self.end_time)

    def is_event_absence(self):
        if self.event.event_type.id != 1:
            return False
        event_act = self.event.eventact
        return event_act.is_absent()
