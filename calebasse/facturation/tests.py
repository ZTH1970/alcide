# -*- coding: utf-8 -*-
import time
from datetime import datetime, date
from dateutil import rrule
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.contrib.auth.models import User

from calebasse.actes.validation import automated_validation, \
    are_all_acts_of_the_day_locked, \
    get_days_with_acts_not_locked
from calebasse.actes.models import Act
from calebasse.agenda.models import EventWithAct
from calebasse.dossiers.models import create_patient, PatientRecord, \
    SessadHealthCareNotification, CmppHealthCareTreatment, CmppHealthCareDiagnostic
from calebasse.dossiers.models import Status
from calebasse.ressources.models import ActType, Service, WorkerType
from calebasse.personnes.models import Worker

from list_acts import (list_acts_for_billing_CAMSP,
    list_acts_for_billing_SESSAD, list_acts_for_billing_CMPP,
    list_acts_for_billing_CMPP_2)

from models import add_price, PricePerAct, Invoicing


class FacturationTest(TestCase):
    fixtures = ['services', 'filestates']
    def setUp(self):
        self.creator = User.objects.create(username='John')

        self.wtype = WorkerType.objects.create(name='ElDoctor', intervene=True)
        self.therapist1 = Worker.objects.create(first_name='Bob', last_name='Leponge', type=self.wtype)
        self.therapist2 = Worker.objects.create(first_name='Jean', last_name='Valjean', type=self.wtype)
        self.therapist3 = Worker.objects.create(first_name='Pierre', last_name='PaulJacques', type=self.wtype)
        self.act_type = ActType.objects.create(name='trepanation')

    def test_facturation_camsp(self):
        service_camsp = Service.objects.get(name='CAMSP')

        patient_a = create_patient('a', 'A', service_camsp, self.creator, date_selected=datetime(2020, 10, 5))
        act0 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 6, 10, 15),
                end_datetime=datetime(2020, 10, 6, 12, 20))
        status_suivi = Status.objects.filter(services__name='CAMSP').filter(type='SUIVI')[0]
        patient_a.set_state(status_suivi, self.creator, date_selected=datetime(2020, 10, 7))
        act1 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 7, 10, 15),
                end_datetime=datetime(2020, 10, 7, 12, 20))
        act2 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 7, 14, 15),
                end_datetime=datetime(2020, 10, 7, 16, 20))
        act3 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 7, 16, 20),
                end_datetime=datetime(2020, 10, 7, 17, 20))
        status_clos = Status.objects.filter(services__name='CAMSP').filter(type='CLOS')[0]
        patient_a.set_state(status_clos, self.creator, date_selected=datetime(2020, 10, 8))
        act4 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 8, 10, 15),
                end_datetime=datetime(2020, 10, 8, 12, 20))

        patient_b = create_patient('b', 'B', service_camsp, self.creator, date_selected=datetime(2020, 10, 4))
        act5 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_b, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 4, 10, 15),
                end_datetime=datetime(2020, 10, 4, 12, 20))
        act6 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_b, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 5, 10, 15),
                end_datetime=datetime(2020, 10, 5, 12, 20))
        act6.set_state('ABS_EXC', self.creator)
        act7 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_b, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 5, 10, 15),
                end_datetime=datetime(2020, 10, 5, 12, 20))
        act7.switch_billable = True
        act7.save()
        patient_b.set_state(status_suivi, self.creator, date_selected=datetime(2020, 10, 6))
        act8 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_b, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 7, 10, 15),
                end_datetime=datetime(2020, 10, 7, 12, 20))
        act9 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_b, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 7, 14, 15),
                end_datetime=datetime(2020, 10, 7, 16, 20))
        act10 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_b, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 7, 16, 20),
                end_datetime=datetime(2020, 10, 7, 17, 20))
        act11 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_b, [self.therapist3],
                self.act_type, service_camsp, start_datetime=datetime(2020, 10, 8, 10, 15),
                end_datetime=datetime(2020, 10, 8, 12, 20))
        patient_b.set_state(status_clos, self.creator, date_selected=datetime(2020, 10, 9))

        automated_validation(datetime(2020, 10, 5), service_camsp, self.creator)
        automated_validation(datetime(2020, 10, 6), service_camsp, self.creator)
        automated_validation(datetime(2020, 10, 7), service_camsp, self.creator)
        automated_validation(datetime(2020, 10, 8), service_camsp, self.creator)

        not_locked, days_not_locked, not_valide, not_billable, acts_pause, rejected, selected = \
            list_acts_for_billing_CAMSP(datetime(2020, 10, 4), datetime(2020, 10, 8), service_camsp)

        self.assertEqual(len(days_not_locked), 1)

        self.assertTrue(act1 in selected[patient_a])
        self.assertTrue(act2 in selected[patient_a])
        self.assertTrue(act3 in selected[patient_a])
        acts_rejected = [x[0] for x in rejected[patient_a]]
        self.assertTrue(act0 in acts_rejected)
        self.assertTrue(act4 in acts_rejected)

        acts_not_locked = [x[0] for x in not_locked[patient_b]]
        self.assertTrue(act5 in acts_not_locked)
        acts_not_valide = [x[0] for x in not_valide[patient_b]]
        self.assertTrue(act6 in acts_not_valide)
        self.assertTrue(act7 in not_billable[patient_b])
        self.assertTrue(act8 in selected[patient_b])
        self.assertTrue(act9 in selected[patient_b])
        self.assertTrue(act10 in selected[patient_b])
        self.assertTrue(act11 in selected[patient_b])

        states = patient_b.get_states_history()
        patient_b.change_day_selected_of_state(states[2], datetime(2020, 10, 7))
        not_locked, days_not_locked, not_valide, not_billable, acts_pause, rejected, selected = \
            list_acts_for_billing_CAMSP(datetime(2020, 10, 4), datetime(2020, 10, 8), service_camsp)
        acts_not_locked = [x[0] for x in not_locked[patient_b]]
        self.assertTrue(act5 in acts_not_locked)
        acts_not_valide = [x[0] for x in not_valide[patient_b]]
        self.assertTrue(act6 in acts_not_valide)
        self.assertTrue(act7 in not_billable[patient_b])
        acts_rejected = [x[0] for x in rejected[patient_b]]
        self.assertTrue(act8 in acts_rejected)
        self.assertTrue(act9 in acts_rejected)
        self.assertTrue(act10 in acts_rejected)
        self.assertTrue(act11 in acts_rejected)

        states = patient_b.get_states_history()
        patient_b.change_day_selected_of_state(states[2], datetime(2020, 10, 9))
        patient_b.change_day_selected_of_state(states[1], datetime(2020, 10, 8))
        not_locked, days_not_locked, not_valide, not_billable, acts_pause, rejected, selected = \
            list_acts_for_billing_CAMSP(datetime(2020, 10, 4), datetime(2020, 10, 8), service_camsp)
        acts_not_locked = [x[0] for x in not_locked[patient_b]]
        self.assertTrue(act5 in acts_not_locked)
        acts_not_valide = [x[0] for x in not_valide[patient_b]]
        self.assertTrue(act6 in acts_not_valide)
        self.assertTrue(act7 in not_billable[patient_b])
        acts_rejected = [x[0] for x in rejected[patient_b]]
        self.assertTrue(act8 in acts_rejected)
        self.assertTrue(act9 in acts_rejected)
        self.assertTrue(act10 in acts_rejected)
        self.assertTrue(act11 in selected[patient_b])

    def test_facturation_sessad(self):
        service_sessad = Service.objects.get(name='SESSAD DYS')

        patient_a = create_patient('a', 'A', service_sessad, self.creator, date_selected=datetime(2020, 10, 5))
        act0 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_sessad, start_datetime=datetime(2020, 10, 6, 10, 15),
                end_datetime=datetime(2020, 10, 6, 12, 20))
        status_traitement = Status.objects.filter(services__name='SESSAD DYS').filter(type='TRAITEMENT')[0]
        patient_a.set_state(status_traitement, self.creator, date_selected=datetime(2020, 10, 7))
        act1 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_sessad, start_datetime=datetime(2020, 10, 7, 10, 15),
                end_datetime=datetime(2020, 10, 7, 12, 20))
        act2 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_sessad, start_datetime=datetime(2020, 10, 7, 14, 15),
                end_datetime=datetime(2020, 10, 7, 16, 20))
        act3 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_sessad, start_datetime=datetime(2020, 10, 7, 16, 20),
                end_datetime=datetime(2020, 10, 7, 17, 20))
        status_clos = Status.objects.filter(services__name='SESSAD DYS').filter(type='CLOS')[0]
        patient_a.set_state(status_clos, self.creator, date_selected=datetime(2020, 10, 8))
        act4 = EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_sessad, start_datetime=datetime(2020, 10, 8, 10, 15),
                end_datetime=datetime(2020, 10, 8, 12, 20))

        automated_validation(datetime(2020, 10, 6), service_sessad, self.creator)
        automated_validation(datetime(2020, 10, 7), service_sessad, self.creator)
        automated_validation(datetime(2020, 10, 8), service_sessad, self.creator)

        not_locked, days_not_locked, not_valide, not_billable, acts_pause, rejected, missing_valid_notification, selected = \
            list_acts_for_billing_SESSAD(datetime(2020, 10, 4), datetime(2020, 10, 8), service_sessad)
        self.assertEqual(not_locked, {})
        self.assertEqual(not_valide, {})
        self.assertEqual(not_billable, {})
        self.assertEqual(len(rejected[patient_a]), 2)
        self.assertEqual(len(missing_valid_notification[patient_a]), 3)
        self.assertEqual(selected, {})

        SessadHealthCareNotification(patient=patient_a, author=self.creator, start_date=datetime(2020,10,7), end_date=datetime(2021,10,6)).save()
        not_locked, days_not_locked, not_valide, not_billable, acts_pause, rejected, missing_valid_notification, selected = \
            list_acts_for_billing_SESSAD(datetime(2020, 10, 4), datetime(2020, 10, 8), service_sessad)
        self.assertEqual(not_locked, {})
        self.assertEqual(not_valide, {})
        self.assertEqual(not_billable, {})
        self.assertEqual(len(rejected[patient_a]), 2)
        self.assertEqual(missing_valid_notification, {})
        self.assertEqual(len(selected[patient_a]), 3)

    def test_facturation_cmpp(self):
        service_cmpp = Service.objects.get(name='CMPP')

        patient_a = create_patient('a', 'A', service_cmpp, self.creator, date_selected=datetime(2020, 10, 1))
        acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2020, 10, i, 10, 15),
                end_datetime=datetime(2020, 10, i, 12, 20)) for i in range (1, 32)]
        status_accueil = Status.objects.filter(services__name='CMPP').filter(type='ACCUEIL')[0]
        status_diagnostic = Status.objects.filter(services__name='CMPP').filter(type='DIAGNOSTIC')[0]
        status_traitement = Status.objects.filter(services__name='CMPP').filter(type='TRAITEMENT')[0]

        self.assertEqual(patient_a.get_state().status, status_accueil)
        automated_validation(datetime(2020, 10, 1), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_diagnostic)
        automated_validation(datetime(2020, 10, 2), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_diagnostic)
        automated_validation(datetime(2020, 10, 3), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_diagnostic)
        automated_validation(datetime(2020, 10, 4), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_diagnostic)
        automated_validation(datetime(2020, 10, 5), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_diagnostic)
        automated_validation(datetime(2020, 10, 6), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_diagnostic)
        automated_validation(datetime(2020, 10, 7), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_traitement)
        automated_validation(datetime(2020, 10, 8), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_traitement)
        automated_validation(datetime(2020, 10, 9), service_cmpp, self.creator)
        patient_a = PatientRecord.objects.get(id=patient_a.id)
        self.assertEqual(patient_a.get_state().status, status_traitement)
        for i in range(10, 32):
            automated_validation(datetime(2020, 10, i), service_cmpp, self.creator)
            patient_a = PatientRecord.objects.get(id=patient_a.id)
            self.assertEqual(patient_a.get_state().status, status_traitement)

        acts_2 = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient_a, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2020, 11, i, 10, 15),
                end_datetime=datetime(2020, 11, i, 12, 20)) for i in range (1, 31)]
        for i in range(1, 31):
            automated_validation(datetime(2020, 11, i), service_cmpp, self.creator)
            patient_a = PatientRecord.objects.get(id=patient_a.id)
            self.assertEqual(patient_a.get_state().status, status_traitement)

        self.assertEqual(get_days_with_acts_not_locked(datetime(2020, 10, 1), datetime(2020, 11, 30)), [])

        acts = acts + acts_2

        hct = CmppHealthCareTreatment(patient=patient_a, start_date=datetime(2020, 10, 7), author=self.creator)
        hct.save()
        hct.add_prolongation()

        billing_cmpp = list_acts_for_billing_CMPP_2(datetime(2020, 11, 30), service_cmpp)

        self.assertEqual(len(billing_cmpp[5][patient_a]), 6)
        self.assertEqual(len(billing_cmpp[6][patient_a]), 40)
        self.assertEqual(len(billing_cmpp[7][patient_a]), 15)


    def test_prices(self):
        price_o = add_price(120, date(2012, 10, 1))
        self.assertEqual(PricePerAct.get_price(), 120)
        price_o = add_price(130, date.today())
        self.assertEqual(PricePerAct.get_price(date.today() + relativedelta(days=-1)), 120)
        self.assertEqual(PricePerAct.get_price(date.today()), 130)
        self.assertEqual(PricePerAct.get_price(date.today() + relativedelta(days=1)), 130)
#        price_o = add_price(140, date(day=27, month=11, year=2012))
        price_o = add_price(140, date.today() + relativedelta(days=1))
        self.assertEqual(PricePerAct.get_price(date.today() + relativedelta(days=-1)), 120)
        self.assertEqual(PricePerAct.get_price(date.today()), 130)
        self.assertEqual(PricePerAct.get_price(date.today() + relativedelta(days=1)), 140)
        self.assertEqual(PricePerAct.get_price(date.today() + relativedelta(days=2)), 140)

    def test_invoicing(self):
        service_cmpp = Service.objects.get(name='CMPP')
        price_o = add_price(120, date(2012, 10, 1))


        patients = []
        for j in range(2):
            patients.append(create_patient(str(j), str(j), service_cmpp, self.creator, date_selected=datetime(2012, 10, 1)))
            acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patients[j], [self.therapist3],
                    self.act_type, service_cmpp, start_datetime=datetime(2012, 10, i, 10, 15),
                    end_datetime=datetime(2012, 10, i, 12, 20)) for i in range (1, 32)]
            acts_2 = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patients[j], [self.therapist3],
                    self.act_type, service_cmpp, start_datetime=datetime(2012, 11, i, 10, 15),
                    end_datetime=datetime(2012, 11, i, 12, 20)) for i in range (1, 31)]
            hct = CmppHealthCareTreatment(patient=patients[j], start_date=datetime(2012, 10, 7), author=self.creator)
            hct.save()
            hct.add_prolongation()

        for i in range(1, 32):
            automated_validation(datetime(2012, 10, i), service_cmpp, self.creator)
        for i in range(1, 31):
            automated_validation(datetime(2012, 11, i), service_cmpp, self.creator)

        self.assertEqual(get_days_with_acts_not_locked(datetime(2012, 10, 1), datetime(2012, 11, 30)), [])
        invoicing = Invoicing.objects.create(service=service_cmpp, seq_id=666, start_date=date.today())
        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate()

        self.assertEqual(len_patients, 2)
        self.assertEqual(len_invoices, 4)
        self.assertEqual(len_invoices_hors_pause, 4)
        self.assertEqual(len_acts_invoiced, 92) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 92) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 2)
        self.assertEqual(len_patient_invoiced_hors_pause, 2)
        self.assertEqual(len_acts_lost, 30)
        self.assertEqual(len_patient_with_lost_acts, 2)

        patients[1].pause = True
        patients[1].save()

        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate()

        self.assertEqual(len_patients, 2)
        self.assertEqual(len_invoices, 4)
        self.assertEqual(len_invoices_hors_pause, 2)
        self.assertEqual(len_acts_invoiced, 92) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 46) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 2)
        self.assertEqual(len_patient_invoiced_hors_pause, 1)
        self.assertEqual(len_acts_lost, 30)
        self.assertEqual(len_patient_with_lost_acts, 2)

        invoicing_next = invoicing.close(date(day=30, month=11, year=2012))

        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate(commit=True)

        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate()

        self.assertEqual(len_patients, 1)
        self.assertEqual(len_invoices, 2)
        self.assertEqual(len_acts_invoiced, 46)

        patients[1].pause = False
        patients[1].save()
        invoicing_next.close(date(day=2, month=12, year=2012))

        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing_next.get_stats_or_validate()

        self.assertEqual(len_patients, 2)
        self.assertEqual(len_invoices, 2)
        self.assertEqual(len_acts_invoiced, 46)

    def test_invoicing2(self):
        service_cmpp = Service.objects.get(name='CMPP')
        price_o = add_price(120, date(2012, 10, 1))


        patient = create_patient('A', 'a', service_cmpp, self.creator, date_selected=datetime(2012, 10, 1))
        acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 10, i, 10, 15),
                end_datetime=datetime(2012, 10, i, 12, 20)) for i in range (1, 32)]
        hct = CmppHealthCareTreatment(patient=patient, start_date=datetime(2011, 11, 7), author=self.creator)
        hct.save()
        hct.add_prolongation()

        for i in range(1, 32):
            automated_validation(datetime(2012, 10, i), service_cmpp, self.creator)

        self.assertEqual(get_days_with_acts_not_locked(datetime(2012, 10, 1), datetime(2012, 11, 30)), [])
        invoicing = Invoicing.objects.create(service=service_cmpp, seq_id=666, start_date=date.today())
        invoicing_next = invoicing.close(date(day=1, month=11, year=2012))
        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate(commit=True)

        self.assertEqual(len_patients, 1)
        self.assertEqual(len_invoices, 2)
        self.assertEqual(len_invoices_hors_pause, 2)
        self.assertEqual(len_acts_invoiced, 31) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 31) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 1)
        self.assertEqual(len_patient_invoiced_hors_pause, 1)
        self.assertEqual(len_acts_lost, 0)
        self.assertEqual(len_patient_with_lost_acts, 0)


        acts_2 = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 11, i, 10, 15),
                end_datetime=datetime(2012, 11, i, 12, 20)) for i in range (1, 31)]

        for i in range(1, 31):
            automated_validation(datetime(2012, 11, i), service_cmpp, self.creator)

        hct = CmppHealthCareTreatment(patient=patient, start_date=datetime(2012, 11, 7), author=self.creator)
        hct.save()

        # 6 sur hct 1
        # 24 sur hct 2

        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing_next.get_stats_or_validate(commit=True)

        self.assertEqual(len_patients, 1)
        self.assertEqual(len_invoices, 1)
        self.assertEqual(len_invoices_hors_pause, 1)
        self.assertEqual(len_acts_invoiced, 30) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 30) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 1)
        self.assertEqual(len_patient_invoiced_hors_pause, 1)
        self.assertEqual(len_acts_lost, 0)
        self.assertEqual(len_patient_with_lost_acts, 0)


    def test_change_state(self):
        service_cmpp = Service.objects.get(name='CMPP')
        price_o = add_price(120, date(2012, 10, 1))


        patient = create_patient('A', 'a', service_cmpp, self.creator, date_selected=datetime(2012, 10, 1))

        self.assertEqual(patient.last_state.status.type, "ACCUEIL")

        EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 10, 1, 10, 15),
                end_datetime=datetime(2012, 10, 1, 12, 20))

        automated_validation(datetime(2012, 10, 1), service_cmpp, self.creator)
        patient =  PatientRecord.objects.get(id=patient.id)

        self.assertEqual(patient.last_state.status.type, "DIAGNOSTIC")
        self.assertEqual(patient.last_state.date_selected, datetime(2012, 10, 1, 0, 0))

        acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 10, i, 10, 15),
                end_datetime=datetime(2012, 10, i, 12, 20)) for i in range (2, 32)]

        for i in range(2, 32):
            automated_validation(datetime(2012, 10, i), service_cmpp, self.creator)

        patient =  PatientRecord.objects.get(id=patient.id)
        self.assertEqual(patient.last_state.status.type, "TRAITEMENT")
        self.assertEqual(patient.last_state.date_selected, datetime(2012, 10, 7, 0, 0))

        patient = create_patient('B', 'b', service_cmpp, self.creator, date_selected=datetime(2012, 10, 1))

        self.assertEqual(patient.last_state.status.type, "ACCUEIL")

        EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 10, 1, 10, 15),
                end_datetime=datetime(2012, 10, 1, 12, 20))

        automated_validation(datetime(2012, 10, 1), service_cmpp, self.creator)
        patient =  PatientRecord.objects.get(id=patient.id)

        self.assertEqual(patient.last_state.status.type, "DIAGNOSTIC")
        self.assertEqual(patient.last_state.date_selected, datetime(2012, 10, 1, 0, 0))

        status = Status.objects.filter(type="CLOS").\
                filter(services__name='CMPP')[0]
        patient.set_state(status, self.creator, date_selected=datetime(2012, 12, 9, 0, 0))

        self.assertEqual(patient.last_state.status.type, "CLOS")
        self.assertEqual(patient.last_state.date_selected, datetime(2012, 12, 9, 0, 0))

        acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 10, i, 10, 15),
                end_datetime=datetime(2012, 10, i, 12, 20)) for i in range (2, 32)]

        for i in range(2, 32):
            automated_validation(datetime(2012, 10, i), service_cmpp, self.creator)

        patient =  PatientRecord.objects.get(id=patient.id)
        self.assertEqual(patient.last_state.status.type, "CLOS")
        self.assertEqual(patient.last_state.date_selected, datetime(2012, 12, 9, 0, 0))

    def test_change_hc_number(self):

        service_cmpp = Service.objects.get(name='CMPP')
        price_o = add_price(120, date(2012, 10, 1))

        patient = create_patient('A', 'a', service_cmpp, self.creator, date_selected=datetime(2012, 10, 1))
        acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 10, i, 10, 15),
                end_datetime=datetime(2012, 10, i, 12, 20)) for i in range (1, 4)]

        for i in range(1, 4):
            automated_validation(datetime(2012, 10, i), service_cmpp, self.creator)

        invoicing = Invoicing.objects.create(service=service_cmpp, seq_id=666, start_date=date.today())
        invoicing_next = invoicing.close(date(day=4, month=10, year=2012))
        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate(commit=True)

        self.assertEqual(len_patients, 1)
        self.assertEqual(len_invoices, 1)
        self.assertEqual(len_invoices_hors_pause, 1)
        self.assertEqual(len_acts_invoiced, 3) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 3) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 1)
        self.assertEqual(len_patient_invoiced_hors_pause, 1)
        self.assertEqual(len_acts_lost, 0)
        self.assertEqual(len_patient_with_lost_acts, 0)

        hcd = CmppHealthCareDiagnostic.objects.\
            filter(patient=patient).latest('start_date')

        self.assertEqual(hcd.get_nb_acts_cared(), 3)

        try:
            hcd.set_act_number(2)
            raise
        except:
            pass

        hcd.set_act_number(5)

        acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 10, i, 10, 15),
                end_datetime=datetime(2012, 10, i, 12, 20)) for i in range (4, 32)]

        for i in range(4, 32):
            automated_validation(datetime(2012, 10, i), service_cmpp, self.creator)

        invoicing = Invoicing.objects.create(service=service_cmpp, start_date=date.today())
        invoicing_next = invoicing.close(date(day=1, month=11, year=2012))
        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate(commit=True)

        self.assertEqual(len_patients, 1)
        self.assertEqual(len_invoices, 1)
        self.assertEqual(len_invoices_hors_pause, 1)
        self.assertEqual(len_acts_invoiced, 2) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 2) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 1)
        self.assertEqual(len_patient_invoiced_hors_pause, 1)
        self.assertEqual(len_acts_lost, 26)
        self.assertEqual(len_patient_with_lost_acts, 1)

        hct = CmppHealthCareTreatment(patient=patient, start_date=datetime(2012, 10, 1), author=self.creator)
        hct.save()

        invoicing = Invoicing.objects.create(service=service_cmpp, start_date=date.today())
        invoicing_next = invoicing.close(date(day=2, month=11, year=2012))
        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate(commit=True)

        self.assertEqual(len_patients, 1)
        self.assertEqual(len_invoices, 1)
        self.assertEqual(len_invoices_hors_pause, 1)
        self.assertEqual(len_acts_invoiced, 26) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 26) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 1)
        self.assertEqual(len_patient_invoiced_hors_pause, 1)
        self.assertEqual(len_acts_lost, 0)
        self.assertEqual(len_patient_with_lost_acts, 0)

        try:
            hct.set_act_number(24)
            raise
        except:
            pass

        hct.set_act_number(28)

        acts = [ EventWithAct.objects.create_patient_appointment(self.creator, 'RDV', patient, [self.therapist3],
                self.act_type, service_cmpp, start_datetime=datetime(2012, 11, i, 10, 15),
                end_datetime=datetime(2012, 11, i, 12, 20)) for i in range (1, 4)]

        for i in range(1, 4):
            automated_validation(datetime(2012, 11, i), service_cmpp, self.creator)

        invoicing = Invoicing.objects.create(service=service_cmpp, start_date=date.today())
        invoicing_next = invoicing.close(date(day=3, month=11, year=2012))
        (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = invoicing.get_stats_or_validate(commit=True)

        self.assertEqual(len_patients, 1)
        self.assertEqual(len_invoices, 1)
        self.assertEqual(len_invoices_hors_pause, 1)
        self.assertEqual(len_acts_invoiced, 2) # tous les actes billed
        self.assertEqual(len_acts_invoiced_hors_pause, 2) # tous les actes billed - les acts qui ne seront pas billed à cause de la pause facturation
        self.assertEqual(len_patient_invoiced, 1)
        self.assertEqual(len_patient_invoiced_hors_pause, 1)
        self.assertEqual(len_acts_lost, 1)
        self.assertEqual(len_patient_with_lost_acts, 1)
