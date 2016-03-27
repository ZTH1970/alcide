# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from models import create_patient, PatientContact
from alcide.dossiers.models import Status
from alcide.ressources.models import Service


class PatientRecordTest(TestCase):

    def test_states(self):
        creator = User.objects.create(username='John')
        for service in Service.objects.all():
            patient = create_patient('John', 'Doe', service, creator)
            for status in Status.objects.filter(services=service):
                patient.set_state(status, creator)


class AgeTest(TestCase):
    def test_unknown(self):
        patient = PatientContact()
        self.assertEqual(patient.age(), "inconnu")

    def test_one_day(self):
        patient = PatientContact()
        patient.birthdate = datetime.date.today() - datetime.timedelta(days=1)
        self.assertEqual(patient.age(), "1 jour")

    def test_three_days(self):
        patient = PatientContact()
        patient.birthdate = datetime.date.today() - datetime.timedelta(days=3)
        self.assertEqual(patient.age(), "3 jours")

    def test_two_months(self):
        patient = PatientContact()
        today = datetime.date.today()
        if today.day > 28:
            # don't run this test on such months, we can't be sure the exact
            # date will exist
            return
        date = today - datetime.timedelta(days=65)
        patient.birthdate = datetime.date(date.year, date.month, today.day)
        self.assertEqual(patient.age(), "2 mois")

    def test_two_months_one_day(self):
        patient = PatientContact()
        today = datetime.date.today()
        if today.day > 28:
            # don't run this test on such months, we can't be sure the exact
            # date will exist
            return
        date = today - datetime.timedelta(days=62)
        patient.birthdate = datetime.date(date.year, date.month, today.day) - datetime.timedelta(days=1)
        self.assertEqual(patient.age(), "2 mois et 1 jour")

    def test_two_months_three_days(self):
        patient = PatientContact()
        today = datetime.date.today()
        if today.day > 25:
            # don't run this test on such months, we can't be sure the exact
            # date will exist
            return
        date = today - datetime.timedelta(days=62)
        patient.birthdate = datetime.date(date.year, date.month, today.day) - datetime.timedelta(days=3)
        self.assertEqual(patient.age(), "2 mois et 3 jours")

    def test_six_months(self):
        patient = PatientContact()
        today = datetime.date.today()
        date = today - datetime.timedelta(days=31*6)
        patient.birthdate = datetime.date(date.year, date.month, date.day)
        self.assertEqual(patient.age(), "6 mois")

    def test_thirtheen_months(self):
        patient = PatientContact()
        today = datetime.date.today()
        date = today - datetime.timedelta(days=31*13)
        patient.birthdate = datetime.date(date.year, date.month, date.day)
        self.assertEqual(patient.age(), "13 mois")

    def test_two_years(self):
        patient = PatientContact()
        today = datetime.date.today()
        date = today
        patient.birthdate = datetime.date(date.year-2, date.month, date.day)
        self.assertEqual(patient.age(), "2 ans")
        self.assertEqual(patient.age(age_format='months_only'), "24 mois")

    def test_two_years_one_month(self):
        patient = PatientContact()
        today = datetime.date.today()
        date = today
        patient.birthdate = datetime.date(date.year-2, date.month, date.day) - \
                datetime.timedelta(days=31)
        self.assertEqual(patient.age(), "2 ans et 1 mois")
        self.assertEqual(patient.age(age_format='months_only'), "25 mois")
