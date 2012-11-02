# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from models import create_patient
from calebasse.ressources.models import Service
from states import *


class PatientRecordTest(TestCase):

    def test_states(self):
        creator = User.objects.create(username='John')
        for service_name in ('CMPP', 'CAMSP', 'SESSAD'):
            service = Service.objects.create(name=service_name)
            patient = create_patient('John', 'Doe', service, creator)
            for state in STATES[service.name].keys()[1:]:
                patient.set_state(state, creator)
