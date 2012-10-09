"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from dateutil import rrule

from calebasse.agenda.managers import EventManager
from calebasse.agenda.models import Occurrence
from calebasse.cale_base.models import CalebasseUser, Patient, ActType, Service

class EventTest(TestCase):

    def test_create_events(self):
        ev_manager = EventManager()
        event = ev_manager.create_event("test 1", 'un test', description='42 42',
            start_datetime=datetime(2012, 10, 20, 13), end_datetime=datetime(2012, 10, 20, 14),
            freq=rrule.WEEKLY, count=3)
        self.assertEqual(str(event), 'test 1')

    def test_create_appointments(self):
        ev_manager = EventManager()
        patient = Patient.objects.create(first_name='Jean', last_name='Le Pouple')
        user1 = User.objects.create(username='Toto')
        user2 = User.objects.create(username='Tintin')
        user3 = User.objects.create(username='JohnDoe')
        therapist1 = CalebasseUser.objects.create(user=user1)
        therapist2 = CalebasseUser.objects.create(user=user2)
        therapist3 = CalebasseUser.objects.create(user=user3)
        act_type = ActType.objects.create(name='trepanation')
        service = Service.objects.create(name='CMPP')
        act_event = ev_manager.create_patient_appointment('RDV avec M X', patient, [therapist1, therapist2],
                act_type, service, start_datetime=datetime(2020, 10, 2, 7, 15),
                end_datetime=datetime(2020, 10, 2, 9, 20),
                freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2040, 10, 2))
        act_event.save()
        act_event2 = ev_manager.create_patient_appointment('RDV avec M Y', patient, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 2, 10, 15),
                end_datetime=datetime(2020, 10, 2, 12, 20),
                freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2021, 10, 2))
        act_event2.save()
        self.assertEqual(str(act_event), 'RDV avec M X')
        self.assertEqual(
                str(Occurrence.objects.daily_occurrences(datetime(2020, 10, 8), [therapist2])),
                '[]'
                )
        self.assertEqual(
                str(Occurrence.objects.daily_occurrences(datetime(2020, 10, 9), [therapist2])),
                '[<Occurrence: RDV avec M X: 2020-10-09T05:15:00+00:00>]'
                )
        self.assertEqual(
                str(Occurrence.objects.daily_occurrences(datetime(2020, 10, 9), [therapist3])),
                '[<Occurrence: RDV avec M Y: 2020-10-09T08:15:00+00:00>]'
                )


