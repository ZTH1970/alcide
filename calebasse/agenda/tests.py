"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from dateutil import rrule

from calebasse.agenda.calendar import Calendar
from calebasse.cale_base.models import CalebasseUser, Patient, ActType, Service

class EventTest(TestCase):

    def test_create_events(self):
        """"""
        calendar = Calendar()
        event = calendar.create_event("test 1", 'un test', description='42 42',
            start_datetime=datetime(2012, 10, 20, 13), end_datetime=datetime(2012, 10, 20, 14),
            freq=rrule.WEEKLY, count=3)
        self.assertEqual(str(event), 'test 1')

    def test_create_appointments(self):
        calendar = Calendar()
        patient = Patient.objects.create(first_name='Jean', last_name='Le Pouple')
        user1 = User.objects.create(username='Toto')
        user2 = User.objects.create(username='Tintin')
        therapist1 = CalebasseUser.objects.create(user=user1)
        therapist2 = CalebasseUser.objects.create(user=user2)
        act_type = ActType.objects.create(name='trepanation')
        service = Service.objects.create(name='CMPP')
        act_event = calendar.create_patient_appointment('RDV avec M X', patient, [therapist1, therapist2],
            act_type, service, start_datetime=datetime(2020, 10, 2, 7, 15),
            end_datetime=datetime(2020, 10, 2, 9, 20),
            freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2040, 10, 2))
        act_event.save()
        self.assertEqual(str(act_event), 'RDV avec M X')


