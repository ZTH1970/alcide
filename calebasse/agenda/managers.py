
from datetime import datetime
from dateutil import rrule

from django.db import models

from calebasse.agenda.conf import default
from calebasse.exceptions import CalebasseException
from calebasse import agenda

__all__ = (
    'EventManager',
    'OccurrenceManager',
)

class EventManager(models.Manager):
    """ This class allows you to manage events, appointment, ...
    """

    def _set_event(self, event, participants=[], description='', service=None,
            start_time=None, end_time=None, note=None, **rrule_params):
        """ Private method to configure an Event or an EventAct
        """
        event.description = description
        event.participants = participants
        event.service = service
        if note is not None:
            event.notes.create(note=note)
        start_time = start_time or datetime.now().replace(
            minute=0, second=0, microsecond=0
        )
        occurence_duration = default.DEFAULT_OCCURRENCE_DURATION
        end_time = end_time or start_time + occurence_duration
        event.add_occurrences(start_time, end_time, **rrule_params)
        event.save()

        return event


    def create_event(self, title, event_type, participants=[], description='',
        service=None, start_datetime=None, end_datetime=None, note=None,
        **rrule_params):
        """
        Convenience function to create an ``Event``, optionally create an 
        ``EventType``, and associated ``Occurrence``s. ``Occurrence`` creation
        rules match those for ``Event.add_occurrences``.

        Args:
            event_type: can be either an ``EventType`` object or the label
            is either created or retrieved.
            participants: List of CalebasseUser
            start_time: will default to the current hour if ``None``
            end_time: will default to ``start_time`` plus
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

        event = self.create(
                title=title,
                event_type=event_type
                )

        return self._set_event(event, participants, service = service,
                start_time = start_datetime, end_time = end_datetime,
                **rrule_params)

    def create_work_event(self, people, weekday, start_time, end_time, until, service=None):
        """ `create_work_event` allows you to add quickly a work event for a user

        Args:
            weekday (str): weekday constants (MO, TU, etc)
            start_date (datetime): start time
            end_date (datetime): end time

        Returns:
            Nothing

        Raise:
            CalebasseException
        """

        if weekday == 'MO':
            weekday = rrule.MO
        elif weekday == 'TU':
            weekday = rrule.TU
        elif weekday == 'WE':
            weekday = rrule.WE
        elif weekday == 'TH':
            weekday = rrule.TH
        elif weekday == 'FR':
            weekday = rrule.FR
        elif weekday == 'SA':
            weekday = rrule.SA
        elif weekday == 'SU':
            weekday = rrule.SU
        else:
            raise CalebasseException("%s is not a valid weekday constants" % day)

        return self.create_event("work %s" % weekday,
                'work_event', service=service, participants=[people],
                freq = rrule.WEEKLY, byweekday = weekday,
                start_datetime = start_time, end_datetime = end_time,
                until = until)

class OccurrenceManager(models.Manager):

    use_for_related_fields = True

    class Meta:
        app_label = 'agenda'

    def daily_occurrences(self, date=None, participants=None):
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
        qs = self.filter(
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
            return qs.filter(event__participants__in=participants)
        else:
            return qs

