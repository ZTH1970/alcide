# -*- coding: utf-8 -*-
import os
import tempfile
import csv

from collections import OrderedDict
from datetime import datetime

from django.db import models

from calebasse.dossiers.models import PatientRecord
from calebasse.personnes.models import Worker
from calebasse.actes.models import Act


STATISTICS = {
    'patients_per_worker_for_period_per_service' :
        {
        'display_name': 'Liste des enfants suivis par intervenant sur une '
            'période pour un service',
        'category': 'Suivi'
    },
}


def patients_per_worker_for_period_per_service(statistic):
    if not (statistic.in_start_date and statistic.in_end_date
            and statistic.in_service):
        return None
    data = []
    data.append(['Intervenants', 'Patients'])
    values = []
    # Get all acts in the period with a patient in the service
    # Make a dic with intervene for keys
    acts = None
    if statistic.in_patients:
        acts = Act.objects.filter(date__gte=statistic.in_start_date,
            date__lte=statistic.in_end_date,
            patient__service=statistic.in_service,
            patient__in=statistic.in_patients)
    else:
        acts = Act.objects.filter(date__gte=statistic.in_start_date,
            date__lte=statistic.in_end_date,
            patient__service=statistic.in_service)
    analyse = dict()
    for act in acts:
        for intervene in act.doctors.all():
            if statistic.in_participants:
                if intervene in statistic.in_participants:
                    analyse.setdefault(intervene, []).append(act.patient)
            else:
                analyse.setdefault(intervene, []).append(act.patient)
    o_analyse = OrderedDict(sorted(analyse.items(), key=lambda t: t[0]))
    for intervene, patients in o_analyse.iteritems():
        values.append([intervene, list(set(patients))])
    data.append(values)
    return data

def render_to_csv(data):
    with tempfile.NamedTemporaryFile(delete=False) as temp_out_csv:
        try:
            writer = csv.writer(temp_out_csv, delimiter=';', quotechar='|',
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(data[0])
            for d in data[1]:
                writer.writerow(d)
            return temp_out_csv.name
        except:
            if delete:
                try:
                    os.unlink(temp_out_pdf.name)
                except:
                    pass
            raise

class Statistic(models.Model):
    patients = models.ManyToManyField('dossiers.PatientRecord',
            null=True, blank=True, default=None)
    participants = models.ManyToManyField('personnes.People',
            null=True, blank=True, default=None)

    def __init__(self, name=None, inputs=dict()):
        self.name = name
        params = STATISTICS.get(name, {})
        self.display_name = params['display_name']
        self.category = params['category']
        self.inputs = inputs
        self.in_participants = list()
        participants = inputs.get('participants')
        if participants:
            p_str_ids = [p for p in participants.split('|') if p]
            for str_id in p_str_ids:
                try:
                    self.in_participants.append(Worker.objects.get(pk=int(str_id)))
                except:
                    pass
        self.in_patients = list()
        patients = inputs.get('patients')
        if patients:
            p_str_ids = [p for p in patients.split('|') if p]
            for str_id in p_str_ids:
                try:
                    self.in_patients.append(PatientRecord.objects.get(pk=int(str_id)))
                except:
                    pass
        self.in_service = inputs.get('service')
        self.in_start_date = None
        try:
            self.in_start_date = datetime.strptime(inputs.get('start_date'),
                "%d/%m/%Y")
        except:
            pass
        self.in_end_date = None
        try:
            self.in_end_date = datetime.strptime(inputs.get('end_date'),
                "%d/%m/%Y")
        except:
            pass

    def get_data(self):
        func = globals()[self.name]
        return func(self)

    def get_file(self):
        data = self.get_data()
        return render_to_csv(data)
