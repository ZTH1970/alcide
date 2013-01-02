# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv
import codecs
import string
import random
from datetime import datetime, time

import django.core.management
import calebasse.settings
django.core.management.setup_environ(calebasse.settings)

from django.contrib.auth.models import User
from calebasse.actes.models import EventAct
from calebasse.agenda.models import Event, EventType
from calebasse.dossiers.models import PatientRecord, Status, FileState
from calebasse.ressources.models import Service
from calebasse.personnes.models import Worker, Holiday, UserWorker
from calebasse.ressources.models import WorkerType, TransportCompany


f = "./scripts/transports.csv"

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
    csvfile = open(f, 'rb')
    csvlines = UnicodeReader(csvfile, delimiter=';', quotechar='|',encoding='utf-8')
    csvlines.next()
    for line in csvlines:
        TransportCompany(name=line[0],
        address = line[1],
        address_complement = line[2],
        zip_code = line[3],
        city = line[4],
        phone = line[5],
        fax = line[6],
        email = line[7],
        correspondant = line[8],
        old_camsp_id = line[9],
        old_cmpp_id = line[10],
        old_sessad_dys_id = line[11],
        old_sessad_ted_id = line[12]
        ).save()


if __name__ == "__main__":
    main()
