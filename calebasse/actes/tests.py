# -*- coding: utf-8 -*-
from datetime import datetime, date

from django.test import TestCase
from django.contrib.auth.models import User

from validation import automated_validation, are_all_acts_of_the_day_locked, \
    get_days_with_acts_not_locked
from calebasse.dossiers.models import create_patient
from calebasse.agenda.models import EventWithAct
from calebasse.ressources.models import ActType, Service, WorkerType
from calebasse.personnes.models import Worker


class ActTest(TestCase):
    fixtures = ['services', 'filestates']
    def test_act_validation(self):
        wtype = WorkerType.objects.create(name='ElDoctor', intervene=True)
        therapist1 = Worker.objects.create(first_name='Bob', last_name='Leponge', type=wtype)
        therapist2 = Worker.objects.create(first_name='Jean', last_name='Valjean', type=wtype)
        therapist3 = Worker.objects.create(first_name='Pierre', last_name='PaulJacques', type=wtype)
        act_type = ActType.objects.create(name='trepanation')
        service = Service.objects.get(name='CMPP')

        creator = User.objects.create(username='John')
        patient = create_patient('John', 'Doe', service, creator)
        patient2 = create_patient('Jimmy', 'Claff', service, creator)
        patient3 = create_patient('Bouba', 'Lourson', service, creator)

        act_event = EventWithAct.objects.create_patient_appointment(creator, 'RDV avec M X', patient,
                [therapist1, therapist2], act_type, service,
                start_datetime=datetime(2020, 10, 2, 7, 15),
                end_datetime=datetime(2020, 10, 2, 9, 20),
                periodicity=1, until=date(2020, 10, 2))
        act_event2 = EventWithAct.objects.create_patient_appointment(creator, 'RDV avec M Y', patient, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 2, 10, 15),
                end_datetime=datetime(2020, 10, 2, 12, 20),
                periodicity=1, until=date(2020, 10, 2))
        act_event3 = EventWithAct.objects.create_patient_appointment(creator, 'RDV avec M X', patient2,
                [therapist1, therapist2], act_type, service,
                start_datetime=datetime(2020, 10, 2, 7, 15),
                end_datetime=datetime(2020, 10, 2, 9, 20),
                periodicity=1, until=date(2020, 10, 2))
        act_event4 = EventWithAct.objects.create_patient_appointment(creator, 'RDV avec M Y', patient3, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 2, 10, 15),
                end_datetime=datetime(2020, 10, 2, 12, 20),
                periodicity=1, until=date(2020, 10, 2))
        act_event5 = EventWithAct.objects.create_patient_appointment(creator, 'RDV avec M Y', patient3, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 3, 10, 15),
                end_datetime=datetime(2020, 10, 3, 12, 20),
                periodicity=1, until=date(2020, 10, 2))
        act_event6 = EventWithAct.objects.create_patient_appointment(creator, 'RDV avec M Z', patient, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 2, 10, 15),
                end_datetime=datetime(2020, 10, 2, 12, 20),
                periodicity=1, until=date(2020, 10, 2))
        act_event7 = EventWithAct.objects.create_patient_appointment(creator, 'RDV avec M Z', patient, [therapist3],
                act_type, service, start_datetime=datetime(2020, 10, 4, 10, 15),
                end_datetime=datetime(2020, 10, 4, 12, 20),
                periodicity=1, until=date(2020, 10, 4))

        act_event3.act.set_state('ABS_EXC', creator)
        act_event6.act.set_state('VALIDE', creator)

        result = automated_validation(date(2020, 10, 2), service, creator, commit=False)
        self.assertEqual(result, (5,2,2,0,1,0,0,0,0,0,0,0))
        self.assertTrue(act_event.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event2.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event3.act.is_state('ABS_EXC'))
        self.assertTrue(act_event4.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event5.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event6.act.is_state('VALIDE'))

        result = automated_validation(date(2020, 10, 2), service, creator)
        self.assertEqual(result, (5,2,2,0,1,0,0,0,0,0,0,0))

        self.assertTrue(act_event.act.is_state('VALIDE'))
        self.assertTrue(act_event2.act.is_state('ACT_DOUBLE'))
        self.assertTrue(act_event3.act.is_state('ABS_EXC'))
        self.assertTrue(act_event4.act.is_state('VALIDE'))
        self.assertTrue(act_event5.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event6.act.is_state('ACT_DOUBLE'))

        self.assertTrue(are_all_acts_of_the_day_locked(datetime(2020, 10, 2, 12, 20)))
        self.assertFalse(are_all_acts_of_the_day_locked(datetime(2020, 10, 3, 12, 20)))
        self.assertFalse(are_all_acts_of_the_day_locked(datetime(2020, 10, 4, 12, 20)))
        self.assertEqual(get_days_with_acts_not_locked(datetime(2020, 10, 2), datetime(2020, 10, 4)),
            [date(2020, 10, 3), date(2020, 10, 4)])

        result = automated_validation(datetime(2020, 10, 2, 12, 20), service, creator, commit=False)
        self.assertEqual(result, (5,2,2,0,1,0,0,0,0,0,0,0))
        self.assertTrue(act_event.act.is_state('VALIDE'))
        self.assertTrue(act_event2.act.is_state('ACT_DOUBLE'))
        self.assertTrue(act_event3.act.is_state('ABS_EXC'))
        self.assertTrue(act_event4.act.is_state('VALIDE'))
        self.assertTrue(act_event5.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event6.act.is_state('ACT_DOUBLE'))

        result = automated_validation(datetime(2020, 10, 2, 12, 20), service, creator)
        self.assertEqual(result, (5,2,2,0,1,0,0,0,0,0,0,0))
        self.assertTrue(act_event.act.is_state('VALIDE'))
        self.assertTrue(act_event2.act.is_state('ACT_DOUBLE'))
        self.assertTrue(act_event3.act.is_state('ABS_EXC'))
        self.assertTrue(act_event4.act.is_state('VALIDE'))
        self.assertTrue(act_event5.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event6.act.is_state('ACT_DOUBLE'))

        result = automated_validation(datetime(2020, 10, 2, 12, 20), service, creator, commit=False)
        self.assertEqual(result, (5,2,2,0,1,0,0,0,0,0,0,0))
        self.assertTrue(act_event.act.is_state('VALIDE'))
        self.assertTrue(act_event2.act.is_state('ACT_DOUBLE'))
        self.assertTrue(act_event3.act.is_state('ABS_EXC'))
        self.assertTrue(act_event4.act.is_state('VALIDE'))
        self.assertTrue(act_event5.act.is_state('NON_VALIDE'))
        self.assertTrue(act_event6.act.is_state('ACT_DOUBLE'))
