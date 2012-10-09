
from datetime import datetime

from django.db import models

from calebasse.agenda.conf import default
from calebasse import agenda

__all__ = (
    'EventManager',
    'OccurrenceManager',
)

class EventManager(object):
    """ This class allows you to manage events, appointment, ...
    """

    def __set_event(self, event, participants=[], description='', services=[],
            start_time=None, end_time=None, note=None, **rrule_params):
        """ Private method to configure an Event or an ActEvent
        """
        event.description = description
        for participant in participants:
            event.participants.add(participant)
        for service in services:
            event.services.add(service)
        if note is not None:
            event.notes.create(note=note)
        start_time = start_time or datetime.now().replace(
            minute=0, second=0, microsecond=0
        )
        occurence_duration = default.DEFAULT_OCCURRENCE_DURATION
        end_time = end_time or start_time + occurence_duration
        event.add_occurrences(start_time, end_time, **rrule_params)

        return event

    def create_patient_appointment(self, title, patient, participants, act_type,
            service, start_datetime, end_datetime, description='', note=None,
            **rrule_params):
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
            Look at calebasse.agenda.tests.EventTest (test_create_appointments method)
        """
        from calebasse.cale_base.models import ActEvent

        event_type, created = agenda.models.EventType.objects.get_or_create(
                label="patient_appointment"
                )

        act_event = ActEvent.objects.create(
                title=title,
                event_type=event_type,
                patient=patient,
                act_type=act_type,
                )

        if service:
            service = [service]

        return self.__set_event(act_event, participants, description,
                services=service, start_time = start_datetime, end_time = end_datetime,
                note = note, **rrule_params)


    def create_event(self, title, event_type, participants=[], description='',
        services=[], start_datetime=None, end_datetime=None, note=None,
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

        event = agenda.models.Event.objects.create(
                title=title,
                event_type=event_type
                )

        return self.__set_event(event, participants, services = services,
                start_time = start_datetime, end_time = end_datetime,
                **rrule_params)


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

