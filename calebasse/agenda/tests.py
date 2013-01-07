"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime, date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from calebasse.agenda.models import Event, EventType, EventWithAct
from calebasse.dossiers.models import create_patient
from calebasse.ressources.models import ActType, Service, WorkerType
from calebasse.personnes.models import Worker
from calebasse.actes.models import Act

class EventTest(TestCase):
    fixtures = ['services', 'filestates']
    def setUp(self):
        self.creator = User.objects.create(username='John')

    def test_triweekly_events(self):
        event = Event.objects.create(start_datetime=datetime(2012, 10, 20, 13),
                end_datetime=datetime(2012, 10, 20, 13, 30), event_type=EventType(id=2),
                recurrence_periodicity=3, recurrence_end_date=date(2012, 12, 1))
        # Test model
        self.assertEqual(event.timedelta(), timedelta(minutes=30))
        occurences = list(event.all_occurences())
        self.assertEqual(occurences[0].start_datetime,
                datetime(2012, 10, 20, 13))
        self.assertEqual(occurences[0].end_datetime,
                datetime(2012, 10, 20, 13, 30))
        self.assertEqual(occurences[1].start_datetime,
                datetime(2012, 11, 10, 13))
        self.assertEqual(occurences[1].end_datetime,
                datetime(2012, 11, 10, 13, 30))
        self.assertEqual(occurences[2].start_datetime,
                datetime(2012, 12,  1, 13))
        self.assertEqual(occurences[2].end_datetime,
                datetime(2012, 12,  1, 13, 30))
        self.assertEqual(len(occurences), 3)
        self.assertTrue(event.is_recurring())
        self.assertEqual(event.next_occurence(today=date(2012, 10, 21)).start_datetime,
            datetime(2012, 11, 10, 13))
        self.assertEqual(event.next_occurence(today=date(2012, 11,  30)).start_datetime,
            datetime(2012, 12,  1, 13))
        self.assertEqual(event.next_occurence(today=date(2012, 12,  2)), None)
        # Test manager
        i = datetime(2012, 10, 1)
        while i < datetime(2013, 2, 1):
            d = i.date()
            if d in (date(2012, 10, 20), date(2012, 11, 10), date(2012, 12, 1)):
                self.assertEqual(list(Event.objects.for_today(d)), [event], d)
            else:
                self.assertEqual(list(Event.objects.for_today(d)), [], d)
            i += timedelta(days=1)

    def test_odd_week_events(self):
        event = Event.objects.create(start_datetime=datetime(2012, 10, 27, 13),
                end_datetime=datetime(2012, 10, 27, 13, 30), event_type=EventType(id=2),
                recurrence_periodicity=12, recurrence_end_date=date(2012, 11, 10))
        occurences = list(event.all_occurences())
        self.assertEqual(len(occurences), 2)
        self.assertEqual(occurences[0].start_datetime,
                datetime(2012, 10, 27, 13))
        self.assertEqual(occurences[0].end_datetime,
                datetime(2012, 10, 27, 13, 30))
        self.assertEqual(occurences[1].start_datetime,
                datetime(2012, 11, 10, 13))
        self.assertEqual(occurences[1].end_datetime,
                datetime(2012, 11, 10, 13, 30))

    def test_first_week_of_month(self):
        event = Event.objects.create(start_datetime=datetime(2012, 9, 3, 13),
                end_datetime=datetime(2012, 9, 3, 13, 30), event_type=EventType(id=2),
                recurrence_periodicity=6, recurrence_end_date=date(2012, 11, 10))
        occurences = list(event.all_occurences())
        self.assertEqual(len(occurences), 3)
        self.assertEqual(occurences[0].start_datetime,
                datetime(2012, 9, 3, 13))
        self.assertEqual(occurences[0].end_datetime,
                datetime(2012, 9, 3, 13, 30))
        self.assertEqual(occurences[1].start_datetime,
                datetime(2012, 10, 1, 13))
        self.assertEqual(occurences[1].end_datetime,
                datetime(2012, 10, 1, 13, 30))
        self.assertEqual(occurences[2].start_datetime,
                datetime(2012, 11, 5, 13))
        self.assertEqual(occurences[2].end_datetime,
                datetime(2012, 11, 5, 13, 30))

    def test_create_appointments(self):
        service_camsp = Service.objects.get(name='CAMSP')

        patient = create_patient('Jean', 'LEPOULPE', service_camsp, self.creator, date_selected=datetime(2020, 10, 5))
        wtype = WorkerType.objects.create(name='ElDoctor', intervene=True)
        therapist1 = Worker.objects.create(first_name='Bob', last_name='Leponge', type=wtype)
        therapist2 = Worker.objects.create(first_name='Jean', last_name='Valjean', type=wtype)
        act_type = ActType.objects.create(name='trepanation')
        service = Service.objects.create(name='CMPP')
        appointment1 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV avec M X', patient,
                [therapist1, therapist2], act_type, service,
                start_datetime=datetime(2020, 10, 2, 7, 15),
                end_datetime=datetime(2020, 10, 2, 9, 20),
                periodicity=None, until=None)
        self.assertEqual(unicode(appointment1), u'Rdv le 2020-10-02 07:15:00 de Jean LEPOULPE avec Bob LEPONGE, Jean VALJEAN pour trepanation (1)')

    def test_create_recurring_appointment(self):
        service_camsp = Service.objects.get(name='CAMSP')
        patient = create_patient('Jean', 'LEPOULPE', service_camsp, self.creator, date_selected=datetime(2020, 10, 5))
        wtype = WorkerType.objects.create(name='ElDoctor', intervene=True)
        therapist3 = Worker.objects.create(first_name='Pierre', last_name='PaulJacques', type=wtype)
        act_type = ActType.objects.create(name='trepanation')
        service = Service.objects.create(name='CMPP')
        appointment2 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV avec M Y', patient, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 2, 10, 15),
                end_datetime=datetime(2020, 10, 2, 12, 20),
                periodicity=2, until=date(2020, 10, 16))
        occurences = list(appointment2.all_occurences())
        self.assertEqual(len(occurences), 2)
        self.assertEqual(Act.objects.filter(parent_event=appointment2).count(), 0)
        [o.act for o in occurences]
        self.assertEqual(Act.objects.filter(parent_event=appointment2).count(), 2)
        self.assertEqual(occurences[0].act.date, occurences[0].start_datetime.date())
        self.assertEqual(occurences[1].act.date, occurences[1].start_datetime.date())
        appointment2.recurrence_periodicity = None
        appointment2.save()
        self.assertEqual(Act.objects.filter(parent_event=appointment2).count(),
                1)
        appointment2.recurrence_periodicity = 2
        appointment2.recurrence_end_date = date(2020, 10, 16)
        appointment2.save()
        occurences = list(appointment2.all_occurences())
        self.assertEqual(len(occurences), 2)
        self.assertEqual(Act.objects.filter(parent_event=appointment2).count(), 1)
        [o.act for o in occurences]
        self.assertEqual(Act.objects.filter(parent_event=appointment2).count(), 2)
        occurences[1].act.set_state('ANNUL_NOUS', self.creator)
        occurences[0].delete()
        occurences = list(appointment2.all_occurences())
        self.assertEqual(len(occurences), 1)
        self.assertEqual(Act.objects.filter(parent_event=appointment2).count(), 1)

    def test_weekly_event_with_exception(self):
        '''
           We create a single weekly event for 3 weeks between 2012-10-01
           and 2012-10-15, then we add two exception:
            - a change on the date for the second occurrence,
            - a cancellation for the third occurrence.
        '''
        event = Event.objects.create(start_datetime=datetime(2012, 10, 1, 13),
                end_datetime=datetime(2012, 10, 1, 13, 30), event_type=EventType(id=2),
                recurrence_periodicity=1, recurrence_end_date=date(2012, 10, 15))
        exception1 = Event.objects.create(start_datetime=datetime(2012, 10, 9, 13, 30),
                end_datetime=datetime(2012, 10, 9, 14), event_type=EventType(id=2),
                exception_to=event, exception_date=date(2012, 10, 8))
        exception2 = Event.objects.create(start_datetime=datetime(2012, 10, 15, 13, 30),
                end_datetime=datetime(2012, 10, 15, 14), event_type=EventType(id=2),
                exception_to=event, exception_date=date(2012, 10, 15), canceled=True)
        a = Event.objects.for_today(date(2012, 10, 1))
        self.assertEqual(list(a), [event])
        b = Event.objects.for_today(date(2012, 10, 8))
        self.assertEqual(list(b), [])
        b1 = Event.objects.for_today(date(2012, 10, 9))
        self.assertEqual(list(b1), [exception1])
        c = Event.objects.for_today(date(2012, 10, 15))
        self.assertEqual(list(c), [])

    def test_weekly_event_exception_creation(self):
        '''
           We create a single weekly event for 3 weeks between 2012-10-01
           and 2012-10-15, then we list its occurrences, modify them and save them:
            - a change on the date for the second occurrence,
            - a cancellation for the third occurrence.
        '''
        wtype = WorkerType.objects.create(name='ElDoctor', intervene=True)
        therapist1 = Worker.objects.create(first_name='Pierre', last_name='PaulJacques', type=wtype)
        therapist2 = Worker.objects.create(first_name='Bob', last_name='Leponge', type=wtype)
        event = Event.objects.create(start_datetime=datetime(2012, 10, 1, 13),
                end_datetime=datetime(2012, 10, 1, 13, 30), event_type=EventType(id=2),
                recurrence_periodicity=1, recurrence_end_date=date(2012, 10, 15))
        event.participants = [ therapist1 ]
        occurrences = list(event.all_occurences())
        self.assertEqual(len(occurrences), 3)
        self.assertEqual(occurrences[1].start_datetime, datetime(2012, 10, 8, 13))
        occurrences[1].start_datetime = datetime(2012, 10, 9, 13)
        occurrences[1].end_datetime = datetime(2012, 10, 9, 13, 30)
        occurrences[1].save()
        occurrences[1].participants = [ therapist1, therapist2 ]
        occurrences[2].canceled = True
        occurrences[2].save()
        a = Event.objects.today_occurrences(date(2012, 10, 1))
        self.assertEqual(list(a), [event])
        self.assertEqual(set(a[0].participants.select_subclasses()), set([therapist1]))
        a1 = list(a[0].all_occurences())
        self.assertEqual(len(a1), 1)
        b = Event.objects.for_today(date(2012, 10, 8))
        self.assertEqual(list(b), [])
        b1 = Event.objects.for_today(date(2012, 10, 9))
        self.assertEqual(list(b1), [occurrences[1]])
        self.assertEqual(set(b1[0].participants.select_subclasses()), set([therapist1, therapist2]))
        c = Event.objects.for_today(date(2012, 10, 15))
        self.assertEqual(list(c), [])
