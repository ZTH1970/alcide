#!/usr/bin/env python

import os
import csv

from datetime import datetime, time

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.contrib.auth.models import User

#from calebasse.actes.models import EventAct
from calebasse.agenda.models import Event, EventType
from calebasse.dossiers.models import PatientRecord, Status, FileState
from calebasse.ressources.models import Service
from calebasse.personnes.models import Worker, Holiday
from calebasse.ressources.models import WorkerType

# Configuration
db_path = "/home/jschneider/apps/calebasse/scripts/20130104-213225/"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
tables = ["rs", "rr"]


# Global mappers. This dicts are used to map a Faure id with a calebasse object.
dossiers = {}

def _to_date(str_date):
    if not str_date:
        return None
    return datetime.strptime(str_date[:-13], "%Y-%m-%d")

def _to_int(str_int):
    if not str_int:
        return None
    return int(str_int)

def discipline_mapper(tables_data, service):
    for line in tables_data['discipline']:
        # Insert workertype
        if not WorkerType.objects.filter(name=line['libelle']):
            WorkerType.objects.create(name=line['libelle'])


def intervenants_mapper(tables_data, service):
    for line in tables_data['intervenants']:
        # Insert workers
        for disp in tables_data['discipline']:
            if disp['id'] == line['discipline']:
                type = WorkerType.objects.get(name=disp['libelle'])
        # TODO : import actif or not
        worker, created = Worker.objects.get_or_create(
                type=type,
                last_name=line['nom'],
                first_name=line['prenom'],
                email=line['email'],
                phone=line['tel'],
                gender=int(line['titre']),
                )
        worker.services.add(service)

def dossiers_mapper(tables_data, service):
    global dossiers
    for line in tables_data['dossiers']:
        status = Status.objects.filter(type="ACCUEIL").filter(services=service)
        creator = User.objects.get(id=1)
        gender = _to_int(line['nais_sexe'])
        if gender == 0:
            gender = None
        # TODO: add more fields
        patient, created = PatientRecord.objects.get_or_create(first_name=line['prenom'],
                last_name=line['nom'], birthdate=_to_date(line['nais_date']),
                twinning_rank=_to_int(line['nais_rang']),
                gender=gender, service=service, creator=creator)
        dossiers[line['id']] = patient

        if not created:
            if not line['ins_date']:
                # Hack when there is no inscription date put 01/01/1970
                line['ins_date'] = "1970-01-01 00:00:00.000"
            fs = FileState.objects.create(status=status[0], author=creator,
                   date_selected=_to_date(line['ins_date']),
                    previous_state=None, patient=patient)
            patient.last_state = fs
            patient.save()
            if line['sor_date']:
                status = Status.objects.filter(type="CLOS").filter(services=service)
                fs = FileState.objects.create(status=status[0], author=creator,
                        date_selected=_to_date(line['sor_date']),
                        previous_state=None, patient=patient)
                patient.last_state = fs
                patient.save()

def rs_mapper(tables_data, service):
    if service.name == "CMPP":
        for line in tables_data['rs']:
            if line['id'] == '32436':
                print line

def rr_mapper(tables_data, service):
    if service.name == "CMPP":
        for line in tables_data['rr']:
            if line['id'] == '650':
                print line


def conge_mapper(tables_data, service):
    """ """
    for line in tables_data['conge']:
        pass

def ev_mapper(tables_data, service):
    """ """
    pass

def notes_mapper(tables_data, service):
    """ """
    pass

def _get_dict(cols, line):
    """"""
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res

tables_data = {}

def main():
    """ """
    for db in dbs:
        if "F_ST_ETIENNE_CMPP" == db:
            service = Service.objects.get(name="CMPP")
        elif "F_ST_ETIENNE_CAMSP" == db:
            service = Service.objects.get(name="CAMSP")
        elif "F_ST_ETIENNE_SESSAD_TED" == db:
            service = Service.objects.get(name="SESSAD TED")
        elif "F_ST_ETIENNE_SESSAD" == db:
            service = Service.objects.get(name="SESSAD DYS")
        for table in tables:
            # TODO: rewrite this part and treat only line by line
            tables_data[table] = None
            csvfile = open(os.path.join(db_path, db, '%s.csv' % table), 'rb')
            csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
            cols = csvlines.next()
            tables_data[table] = []
            for line in csvlines:
                data = _get_dict(cols, line)
                tables_data[table].append(data)
            func = eval("%s_mapper" % table)
            func(tables_data, service)
            csvfile.close()


if __name__ == "__main__":
    main()

