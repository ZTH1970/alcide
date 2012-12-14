#!/usr/bin/env python

import os
import csv

from datetime import datetime

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from calebasse.ressources.models import Service

# Config
db_path = "/home/jschneider/temp/20121213-185146/"

dbs = ["F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD", "F_ST_ETIENNE_SESSAD_TED"]
tables = ["discipline", "intervenants", "notes", "ev", "conge"]


def discipline_mapper(tables_data, service):
    from calebasse.ressources.models import WorkerType
    for line in tables_data['discipline']:
        # Insert workertype
        if not WorkerType.objects.filter(name=line['libelle']):
            WorkerType.objects.create(name=line['libelle'])


def intervenants_mapper(tables_data, service):
    from calebasse.personnes.models import Worker
    from calebasse.ressources.models import WorkerType
    for line in tables_data['intervenants']:
        print line.keys()
        # Insert workers
        for disp in tables_data['discipline']:
            if disp['id'] == line['discipline']:
                type = WorkerType.objects.get(name=disp['libelle'])
#        Worker.objects.create(
#                type=type,
#                last_name=line['nom'],
#                first_name=line=['prenom'],
#                first_name=line=['prenom'],


def conge_mapper(tables_data, service):
    """ """
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

