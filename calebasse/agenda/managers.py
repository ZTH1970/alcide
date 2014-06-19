
from datetime import datetime, timedelta, date, time
from interval import IntervalSet

from django.db.models import Q
from model_utils.managers import InheritanceManager, PassThroughManager, InheritanceQuerySet

from calebasse.agenda.conf import default
from calebasse.utils import weeks_since_epoch, weekday_ranks
from calebasse import agenda

__all__ = (
    'EventManager',
)


class EventQuerySet(InheritanceQuerySet):
    def for_today(self, today=None):
        today = today or date.today()
        excluded = self.filter(exceptions__exception_date=today).values_list('id', flat=True)
        weeks = weeks_since_epoch(today)
        filters = [Q(start_datetime__gte=datetime.combine(today, time()),
               start_datetime__lte=datetime.combine(today, time(23,59,59)),
               recurrence_periodicity__isnull=True,
               canceled=False) ]
        base_q = Q(start_datetime__lte=datetime.combine(today, time(23,59,59)),
                canceled=False,
                recurrence_week_day=today.weekday(),
                recurrence_periodicity__isnull=False) & \
                (Q(recurrence_end_date__gte=today) |
                    Q(recurrence_end_date__isnull=True)) & \
                ~ Q(id__in=excluded)
        # week periods
        for period in range(1, 6):
            filters.append(base_q & Q(recurrence_week_offset=weeks % period,
                recurrence_week_period=period))
        # week parity
        parity = today.isocalendar()[1] % 2
        filters.append(base_q & Q(recurrence_week_parity=parity))
        # week ranks
        filters.append(base_q & Q(recurrence_week_rank__in=weekday_ranks(today)))
        qs = self.filter(reduce(Q.__or__, filters))
        qs = qs.distinct()
        return qs

    def today_occurrences(self, today=None):
        today = today or date.today()
        self = self.for_today(today)
        occurences = ( e.today_occurrence(today) for e in self )
        return sorted(occurences, key=lambda e: e.start_datetime)

    def daily_disponibilities(self, date, events, participant, time_tables,
            holidays):
        '''Slice the day into quarters between 8:00 and 19:00, and returns the
           list of particpants with their status amon free, busy and away for each
           hour and quarters.

           date - the date of day we slice
           occurences - a dictionnary of iterable of events indexed by participants
           participants - an iterable of participants
           time_tables - a dictionnaty of timetable applying for this day indexed by participants
           holidays - a dictionnary of holidays applying for this day indexed by participants
        '''
        result = dict()
        quarter = 0

        events_intervals = IntervalSet((o.to_interval() for o in events if not o.is_event_absence()))

        timetables_intervals = IntervalSet((t.to_interval(date) for t in time_tables))
        holidays_intervals = IntervalSet((h.to_interval(date) for h in holidays))

        start_datetime = datetime(date.year, date.month, date.day, 8, 0)
        end_datetime = datetime(date.year, date.month, date.day, 8, 15)
        while (start_datetime.hour <= 19):

            if not result.has_key(start_datetime.hour):
                result[start_datetime.hour] = [[], [], [], []]
                quarter = 0
            interval = IntervalSet.between(start_datetime, end_datetime, False)
            mins = quarter * 15
            crossed_events = self.overlap_occurences(start_datetime, events)
            if len(crossed_events) > 1:
                result[start_datetime.hour][quarter].append((mins, {'id': participant.id, 'dispo': 'overlap'}))
            elif interval.intersection(events_intervals):
                result[start_datetime.hour][quarter].append((mins, {'id': participant.id, 'dispo': 'busy'}))
            elif interval.intersection(holidays_intervals):
                result[start_datetime.hour][quarter].append((mins, {'id': participant.id, 'dispo': 'busy'}))
            elif not interval.intersection(timetables_intervals):
                result[start_datetime.hour][quarter].append((mins, {'id': participant.id, 'dispo': 'away'}))
            else:
                result[start_datetime.hour][quarter].append((mins, {'id': participant.id, 'dispo': 'free'}))
            quarter += 1
            start_datetime += timedelta(minutes=15)
            end_datetime += timedelta(minutes=15)
        return result

    def overlap_occurences(self, date_time=None, events=None):
        """
        returns the list of overlapping event occurences which do not begin and end
        at the same time and have the same act type
        """
        date_time = date_time or datetime.now()
        if events is None:
            events = self.today_occurrences(date_time.date())
        overlap = filter(lambda e: e.start_datetime <= date_time and e.end_datetime > date_time \
                         and not e.is_absent(), events)
        same_type_events = []
        different_overlap = []
        for event in overlap:
            if different_overlap:
                for e in different_overlap:
                    try:
                        if event.start_datetime == e.start_datetime and \
                           event.end_datetime == e.end_datetime and \
                           event.act_type == e.act_type:
                            continue
                        different_overlap.append(event)
                    except AttributeError:
                        continue
            else:
                different_overlap.append(event)
        return different_overlap


class EventManager(PassThroughManager.for_queryset_class(EventQuerySet),
        InheritanceManager):
    """ This class allows you to manage events, appointment, ...
    """

    def create_event(self, creator, title, event_type, participants=[], description='',
            services=[], start_datetime=None, end_datetime=None, ressource=None, note=None, periodicity=1, until=False, **kwargs):
        """
        Convenience function to create an ``Event``, optionally create an
        ``EventType``.

        Args:
            event_type: can be either an ``EventType`` object or the label
            is either created or retrieved.
            participants: List of CalebasseUser
            start_datetime: will default to the current hour if ``None``
            end_datetime: will default to ``start_datetime`` plus
            default.DEFAULT_EVENT_DURATION hour if ``None``
        Returns:
            Event object
        """
        if isinstance(event_type, str):
            event_type, created = agenda.models.EventType.objects.get_or_create(
                label=event_type
            )
        if not start_datetime:
            now = datetime.now()
            start_datetime = datetime.combine(now.date, time(now.hour))
        if not end_datetime:
            end_datetime = start_datetime + default.DEFAULT_EVENT_DURATION
        if until is False:
            until = start_datetime.date()
        event = self.create(creator=creator,
                title=title, start_datetime=start_datetime,
                end_datetime=end_datetime, event_type=event_type,
                ressource=ressource, recurrence_periodicity=periodicity,
                recurrence_end_date=until, **kwargs)
        event.services = services
        event.participants = participants
        return event

    def next_appointment(self, patient_record):
        qs = self.next_appointments(patient_record)
        if qs:
            return qs[0]
        else:
            return None

    def next_appointments(self, patient_record, today=None):
        from calebasse.actes.models import Act
        acts = Act.objects.next_acts(patient_record, today=today) \
                .filter(parent_event__isnull=False) \
                .select_related()
        return [ a.parent_event.today_occurrence(a.date) for a in acts ]

    def last_appointment(self, patient_record):
        qs = self.last_appointments(patient_record)
        if qs:
            return qs[0]
        else:
            return None

    def last_appointments(self, patient_record, today=None):
        from calebasse.actes.models import Act
        acts = Act.objects.last_acts(patient_record, today=today) \
                .filter(parent_event__isnull=False) \
                .select_related()
        return [ a.parent_event.today_occurrence(a.date) for a in acts ]
