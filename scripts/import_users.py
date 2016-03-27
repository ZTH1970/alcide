# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv
import codecs
import string
import random
from datetime import datetime, time

import django.core.management
import alcide.settings
django.core.management.setup_environ(alcide.settings)

from django.contrib.auth.models import User
from alcide.actes.models import EventAct
from alcide.agenda.models import Event, EventType
from alcide.dossiers.models import PatientRecord, Status, FileState
from alcide.ressources.models import Service
from alcide.personnes.models import Worker, Holiday, UserWorker
from alcide.ressources.models import WorkerType


wt="./scripts/worker_type.csv"
access_worker_enabled="./scripts/access_worker.csv"
worker_only_disabled="./scripts/worker_only.csv"
db_path = "./scripts/20121219-212026"
dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]

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

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="iso8859-15", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

def main():
    '''User and worker'''
    cmpp = Service.objects.get(name="CMPP")
    camsp = Service.objects.get(name="CAMSP")
    sessad_ted = Service.objects.get(name="SESSAD TED")
    sessad_dys = Service.objects.get(name="SESSAD DYS")
    csvfile = open(access_worker_enabled, 'rb')
    csvlines = UnicodeReader(csvfile, delimiter=';', quotechar='|',encoding='utf-8')
    csvlines.next()
    for line in csvlines:
        user = User(username=line[2])
        user.set_password(line[3])
        user.save()

        last_name = line[0]
        first_name = line[1]
        gender = 1
        if line[14] == 'femme':
            gender = 2
        email = line[13]
        type = WorkerType.objects.get(pk=int(line[8]))
        enabled = True
        old_camsp_id = None
        if line[9] != '':
            old_camsp_id = line[9]
        old_cmpp_id = None
        if line[10] != '':
            old_cmpp_id = line[10]
        old_sessad_dys_id = None
        if line[11] != '':
            old_sessad_dys_id = line[11]
        old_sessad_ted_id = None
        if line[12] != '':
            old_sessad_ted_id = line[12]

        worker = Worker(last_name=last_name, first_name=first_name,
            gender=gender, email=email, type=type,
            old_camsp_id=old_camsp_id, old_cmpp_id=old_cmpp_id,
            old_sessad_dys_id=old_sessad_dys_id, old_sessad_ted_id=old_sessad_ted_id,
            enabled=enabled)
        worker.save()
        if line[4] != '':
            worker.services.add(camsp)
        if line[5] != '':
            worker.services.add(cmpp)
        if line[6] != '':
            worker.services.add(sessad_dys)
        if line[7] != '':
            worker.services.add(sessad_ted)
        worker.save()
        UserWorker(user=user,worker=worker).save()


    '''Worker only'''
    csvfile = open(worker_only_disabled, 'rb')
    csvlines = UnicodeReader(csvfile, delimiter=';', quotechar='|',encoding='utf-8')
    csvlines.next()
    for line in csvlines:

        old_camsp_id = None
        old_cmpp_id = None
        old_sessad_dys_id = None
        old_sessad_ted_id = None
        service = line[5]
        if service == 'CAMSP':
            old_camsp_id = line[0]
        elif service == 'CMPP':
            old_cmpp_id = line[0]
        elif service == 'SESSAD DYS':
            old_sessad_dys_id = line[0]
        else:
            old_sessad_ted_id = line[0]
        last_name = line[1]
        first_name = line[2]
        gender = 1
        if line[3] == 'Femme':
            gender = 2
        type = WorkerType.objects.get(pk=int(line[4]))
        enabled = False

        worker = Worker(last_name=last_name, first_name=first_name,
            gender=gender, email=None, type=type,
            old_camsp_id=old_camsp_id, old_cmpp_id=old_cmpp_id,
            old_sessad_dys_id=old_sessad_dys_id, old_sessad_ted_id=old_sessad_ted_id,
            enabled=enabled)
        worker.save()


if __name__ == "__main__":
    main()
