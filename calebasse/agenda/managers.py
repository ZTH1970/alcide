
from datetime import datetime, timedelta
from interval import IntervalSet

from django.db import models
from model_utils.managers import InheritanceManager

from calebasse.agenda.conf import default
from calebasse import agenda

__all__ = (
    'EventManager',
    'OccurrenceManager',
)

class EventManager(InheritanceManager):
    """ This class allows you to manage events, appointment, ...
    """

    def _set_event(self, event, participants=[], description='', services=[],
            start_datetime=None, end_datetime=None, note=None, room=None, **rrule_params):
        """ Private method to configure an Event or an EventAct
        """
        event.description = description
        event.participants = participants
        event.services = services
        event.room = room
        if note is not None:
            event.notes.create(note=note)
        start_datetime = start_datetime or datetime.now().replace(
            minute=0, second=0, microsecond=0
        )
        occurence_duration = default.DEFAULT_OCCURRENCE_DURATION
        end_datetime = end_datetime or start_datetime + occurence_duration
        event.add_occurrences(start_datetime, end_datetime, **rrule_params)
        event.save()

        return event


    def create_event(self, title, event_type, participants=[], description='',
        services=[], start_datetime=None, end_datetime=None, room=None, note=None,
        **rrule_params):
        """
        Convenience function to create an ``Event``, optionally create an 
        ``EventType``, and associated ``Occurrence``s. ``Occurrence`` creation
        rules match those for ``Event.add_occurrences``.

        Args:
            event_type: can be either an ``EventType`` object or the label
            is either created or retrieved.
            participants: List of CalebasseUser
            start_datetime: will default to the current hour if ``None``
            end_datetime: will default to ``start_datetime`` plus
            default.DEFAULT_OCCURRENCE_DURATION hour if ``None``
            freq, count, rrule_params:
            follow the ``dateutils`` API (see http://labix.org/python-dateutil)
        Returns:
            Event object
        """

        if isinstance(event_type, str):
            event_type, created = agenda.models.EventType.objects.get_or_create(
                label=event_type
            )
        event = self.create(title=title, event_type=event_type)

        return self._set_event(event, participants, services = services,
                start_datetime = start_datetime, end_datetime = end_datetime,
                room=room, **rrule_params)

    def create_holiday(self, start_date, end_date, peoples=[], services=[], motive=''):
        event_type, created = agenda.models.EventType.objects.get_or_create(
                label=u"Vacances"
                )
        event = self.create(title="Conge", event_type=event_type)
        start_datetime = datetime(start_date.year, start_date.month, start_date.day)
        end_datetime = datetime(end_date.year, end_date.month, end_date.day, 23, 59)
        return self._set_event(event, peoples, motive, services, start_datetime, end_datetime)

class OccurrenceManager(models.Manager):

    def daily_occurrences(self, date=None, participants=None, services=None,
            event_type=None):
        '''
        Returns a queryset of for instances that have any overlap with a 
        particular day.

        Args:
            date: may be either a datetime.datetime, datetime.date object, or
            ``None``. If ``None``, default to the current day.
            participants: a list of CalebasseUser
        '''
        date = date or datetime.now()
        start = datetime(date.year, date.month, date.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.select_related('event').filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end,
            )
        )

        if participants:
            qs = qs.filter(event__participants__in=participants)
        if services:
            qs = qs.filter(event__services__in=services)
        if event_type:
            qs = qs.filter(event__event_type=event_type)
        return qs

    def daily_disponiblity(self, date, occurrences, participants, time_tables):
        result = dict()
        quater = 0
        occurrences_set = {}
        timetables_set = {}
        for participant in participants:
            occurrences_set[participant.id] = IntervalSet((o.to_interval() for o in occurrences[participant.id]))
            timetables_set[participant.id] = IntervalSet((t.to_interval(date) for t in time_tables[participant.id]))
        start_datetime = datetime(date.year, date.month, date.day, 8, 0)
        end_datetime = datetime(date.year, date.month, date.day, 8, 15)
        while (start_datetime.hour <= 19):
            for participant in participants:
                if not result.has_key(start_datetime.hour):
                    result[start_datetime.hour] = [0, 1, 2, 3]
                    result[start_datetime.hour][0] = []
                    result[start_datetime.hour][1] = []
                    result[start_datetime.hour][2] = []
                    result[start_datetime.hour][3] = []
                    quater = 0

                interval = IntervalSet.between(start_datetime, end_datetime, False)
                if interval.intersection(occurrences_set[participant.id]):
                    result[start_datetime.hour][quater].append({'id': participant.id, 'dispo': 'busy'})
                elif not interval.intersection(timetables_set[participant.id]):
                    result[start_datetime.hour][quater].append({'id': participant.id, 'dispo': 'away'})
                else:
                    result[start_datetime.hour][quater].append({'id': participant.id, 'dispo': 'free'})
            quater += 1
            start_datetime += timedelta(minutes=15)
            end_datetime += timedelta(minutes=15)
        return result

    def next_appoinment(self, patient_record):
        qs = self.filter(start_time__gt=datetime.now()).\
                filter(event__event_type__id=1).\
                prefetch_related('event__eventact').\
                order_by('start_time')
        if qs:
            return qs[0]
        else:
            return None

    def last_appoinment(self, patient_record):
        qs = self.filter(start_time__lt=datetime.now()).\
                filter(event__event_type__id=1).\
                prefetch_related('event__eventact').\
                order_by('-start_time')
        if qs:
            return qs[0]
        else:
            return None

