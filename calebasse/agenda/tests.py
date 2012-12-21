"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime, date
from dateutil import rrule

from calebasse.agenda.models import Occurrence, Event
from calebasse.actes.models import EventAct
from calebasse.dossiers.models import PatientRecord
from calebasse.dossiers.models import create_patient
from calebasse.ressources.models import ActType, Service, WorkerType
from calebasse.personnes.models import Worker

class EventTest(TestCase):
    fixtures = ['services', 'filestates']
    def setUp(self):
        self.creator = User.objects.create(username='John')

    def test_create_events(self):
        event = Event.objects.create_event("test 1", 'un test', description='42 42',
            start_datetime=datetime(2012, 10, 20, 13), end_datetime=datetime(2012, 10, 20, 14),
            freq=rrule.WEEKLY, count=3)
        self.assertEqual(str(event), 'test 1')

    def test_create_appointments(self):
        service_camsp = Service.objects.create(name='CAMSP')

        patient = create_patient('Jean', 'Lepoulpe', service_camsp, self.creator, date_selected=datetime(2020, 10, 5))
        wtype = WorkerType.objects.create(name='ElDoctor', intervene=True)
        therapist1 = Worker.objects.create(first_name='Bob', last_name='Leponge', type=wtype)
        therapist2 = Worker.objects.create(first_name='Jean', last_name='Valjean', type=wtype)
        therapist3 = Worker.objects.create(first_name='Pierre', last_name='PaulJacques', type=wtype)
        act_type = ActType.objects.create(name='trepanation')
        service = Service.objects.create(name='CMPP')
        act_event = EventAct.objects.create_patient_appointment(self.creator, 'RDV avec M X', patient,
                [therapist1, therapist2], act_type, service,
                start_datetime=datetime(2020, 10, 2, 7, 15),
                end_datetime=datetime(2020, 10, 2, 9, 20),
                freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2040, 10, 2))
        act_event2 = EventAct.objects.create_patient_appointment(self.creator, 'RDV avec M Y', patient, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 2, 10, 15),
                end_datetime=datetime(2020, 10, 2, 12, 20),
                freq=rrule.WEEKLY, byweekday=rrule.FR, until=datetime(2021, 10, 2))
        self.assertEqual(str(act_event), 'Rdv le 2020-10-02 07:15:00 de Jean Lepoulpe avec Bob Leponge, Jean Valjean pour trepanation (1)')
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

    def test_create_holiday(self):
        """docstring for test_create_event"""
        wtype = WorkerType.objects.create(name='ElProfessor', intervene=True)
        user = Worker.objects.create(first_name='Jean-Claude', last_name='Van Damme', type=wtype)
        event = Event.objects.create_holiday(date(2012, 12, 12), date(2012,12,30),
                [user], motive='tournage d\'un film')
        self.assertEqual(str(event), 'Conge')
        #event = user.event.occurrence_set.all()[0]
        #self.assertEqual(event.end_time - event.start_time, timedelta(0, 7200))
