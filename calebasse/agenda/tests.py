"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from dateutil import rrule

from calebasse.agenda.models import Occurrence, Event
from calebasse.actes.models import EventAct
from calebasse.dossiers.models import PatientRecord
from calebasse.ressources.models import ActType, Service
from calebasse.personnes.models import Doctor

class EventTest(TestCase):

    def test_create_events(self):
        event = Event.objects.create_event("test 1", 'un test', description='42 42',
            start_datetime=datetime(2012, 10, 20, 13), end_datetime=datetime(2012, 10, 20, 14),
            freq=rrule.WEEKLY, count=3)
        self.assertEqual(str(event), 'test 1')

    def test_create_appointments(self):
        patient = PatientRecord.objects.create(first_name='Jean', last_name='Le Pouple')
        therapist1 = Doctor.objects.create(first_name='Bob', last_name='Leponge')
        therapist2 = Doctor.objects.create(first_name='Jean', last_name='Valjean')
        therapist3 = Doctor.objects.create(first_name='Pierre', last_name='PaulJacques')
        act_type = ActType.objects.create(name='trepanation')
        service = Service.objects.create(name='CMPP')
        act_event = EventAct.objects.create_patient_appointment('RDV avec M X', patient,
                [therapist1, therapist2], act_type, service,
                start_datetime=datetime(2020, 10, 2, 7, 15),
                end_datetime=datetime(2020, 10, 2, 9, 20),
                freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2040, 10, 2))
        act_event2 = EventAct.objects.create_patient_appointment('RDV avec M Y', patient, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 2, 10, 15),
                end_datetime=datetime(2020, 10, 2, 12, 20),
                freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2021, 10, 2))
        self.assertEqual(str(act_event), 'RDV avec M X')
        self.assertEqual(
                str(Occurrence.objects.daily_occurrences(datetime(2020, 10, 8), [therapist2])),
                '[]'
                )
        self.assertEqual(
                str(Occurrence.objects.daily_occurrences(datetime(2020, 10, 9), [therapist2])),
                '[<Occurrence: RDV avec M X: 2020-10-09T07:15:00>]'
                )
        self.assertEqual(
                str(Occurrence.objects.daily_occurrences(datetime(2020, 10, 9), [therapist3])),
                '[<Occurrence: RDV avec M Y: 2020-10-09T10:15:00>]'
                )

    def test_create_work_event(self):
        """docstring for test_create_event"""
        user = Doctor.objects.create(first_name='Jean-Claude', last_name='Van Damme')
        event = Event.objects.create_work_event(user, 'MO', datetime(2016,10,2,10), datetime(2016,10,2,12),
                datetime(2018,1,1))
        self.assertEqual(str(event), 'work MO')
        #event = user.event.occurrence_set.all()[0]
        #self.assertEqual(event.end_time - event.start_time, timedelta(0, 7200))

