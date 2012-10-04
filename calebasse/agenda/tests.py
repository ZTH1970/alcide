"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from datetime import datetime
from dateutil import rrule


class EventTest(TestCase):

    def create_events(self):
        """docstring for create_event"""
        from calebasse.agenda.calendar import Calendar
        from calebasse.cale_base.models import CalebasseUser, Patient, ActType
        self.assertEqual(str(event), 'work MO')
        calendar = Calendar()
        event = calendar.create_event("test 1", 'un test', description='42 42',
            start_datetime=datetime(2012, 10, 20, 13), end_datetime=datetime(2012, 10, 20, 14),
            freq=rrule.WEEKLY, count=3)
        event.save()
        self.assertEqual(str(event), 'work MO')
        patient = Patient(firstname='Jean', lastname='Le Pouple')
        therapist1 = CalebasseUser(firstname='Paul', lastname='Lipoune')
        therapist2 = CalebasseUser(firstname='Gerard', lastname='Bouchard')
        act_type = ActType(name='trepanation')
        patient.save()
        therapist1.save()
        therapist2.save()
        act_type.save()
        act_event = calendar.add_patient_appointment('RDV avec M X', patient, [therapist1, therapist2],
            act_type, start_datetime=datetime(2020, 10, 2, 7, 15), end_datetime=datetime(2020, 10, 2, 9, 20),
            freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2040, 10, 2))
        act_event.save()
