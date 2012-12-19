#!/usr/bin/env python

import os
import csv

from datetime import datetime

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from calebasse.ressources.models import Service
from django.contrib.auth.models import User

# Config
db_path = "/home/jschneider/temp/20121218-123613/"

dbs = ["F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD", "F_ST_ETIENNE_SESSAD_TED"]
#tables = ["discipline", "intervenants", "notes", "ev", "conge"]
tables = ["discipline", "intervenants", "dossiers", "rs", "notes", "ev", "conge"]


def _to_date(str_date):
    if not str_date:
        return None
    print str_date
    return datetime.strptime(str_date[:-13], "%Y-%m-%d")

def discipline_mapper(tables_data, service):
    from calebasse.ressources.models import WorkerType
    for line in tables_data['discipline']:
        # Insert workertype
        print "ICI"
        print line.keys()
        if not WorkerType.objects.filter(name=line['libelle']):
            WorkerType.objects.create(name=line['libelle'])


def intervenants_mapper(tables_data, service):
    from calebasse.personnes.models import Worker
    from calebasse.ressources.models import WorkerType
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
    from calebasse.dossiers.models import PatientRecord
    from calebasse.dossiers.models import Status, FileState
    for line in tables_data['dossiers']:
        print "ID : " + line['id']
        print "Inscription : " + line['ins_date']
        print "Sortie : " + line['sor_date']
        print "Naissance : "  + line['nais_date']
        status = Status.objects.filter(type="ACCUEIL").filter(services=service)
        creator = User.objects.get(id=1)
        if not line['nais_sexe']:
            gender = None
        else:
            gender = int(line['nais_sexe'])
        if gender == 0:
            gender = None
        patient, created = PatientRecord.objects.get_or_create(first_name=line['nom'],
                last_name=line['prenom'], birthdate=_to_date(line['nais_date']),
                twinning_rank=int(line['nais_rang']),
                gender=gender, service=service, creator=creator)

        if not created:
            if not line['ins_date']:
                # TODO: hack when there is not inscription date put 01/01/1900
                line['ins_date'] = "1900-01-01 00:00:00.000"
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
    pass

def conge_mapper(tables_data, service):
    """ """
    from calebasse.personnes.models import Holiday
    # ['base_origine', 'motif', 'date_conge', 'date_fin', 'id', 'thera_id', 'date_debut']
    for line in tables_data['conge']:
        print line

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
            tables_data[table] = None
            csvfile = open(os.path.join(db_path, db, '%s.csv' % table), 'rb')
            csvlines = csv.reader(csvfile, delimiter=',', quotechar='"')
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

