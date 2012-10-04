
from django.db import models
from django.contrib.auth.models import User

from calebasse.agenda.calendar import Calendar
from calebasse.exceptions import CalebasseException
from dateutil import rrule

class CalebasseUser(User):

    class Meta:
        app_label = 'cale_base'

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    services = models.ManyToManyField('ActType')
    work_event = models.ManyToManyField('agenda.Event', related_name='work_events')
    holidays = models.ManyToManyField('agenda.Event', related_name='holidays')

    def add_work_event(self, weekday, start_time, end_time, until, services=[]):
        """ `add_work_event` allows you to add quickly a work event for a user

        Args:
            weekday (str): weekday constants (MO, TU, etc)
            start_date (datetime): start time
            end_date (datetime): end time
            services (list): list of cale_base.models.Service objects

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

        cal = Calendar()
        self.event = cal.create_event("work %s" % weekday,
                'work_event', services=services,
                freq = rrule.WEEKLY, byweekday = weekday,
                start_datetime = start_time, end_datetime = end_time,
                until = until)


