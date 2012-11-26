# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from models import create_patient
from calebasse.dossiers.models import Status
from calebasse.ressources.models import Service, Service


class PatientRecordTest(TestCase):

    def test_states(self):
        creator = User.objects.create(username='John')
        for service in Service.objects.all():
            patient = create_patient('John', 'Doe', service, creator)
            for status in Status.objects.filter(services=service):
                patient.set_state(status, creator)
