import ipdb
# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv
import logging
import random

from copy import deepcopy
from datetime import datetime, timedelta


import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from calebasse.agenda.models import Event, EventType
from calebasse.personnes.models import Worker, UserWorker
from calebasse.ressources.models import Service, WorkerType

from scripts.import_rs import PERIOD_FAURE_NOUS
from scripts.utils import _get_dict

# Configuration
db_path = "./scripts/20130104-213225"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
#tables = ['intervenants']

# Global mappers. This dicts are used to map a Faure id with a calebasse object.
tables_data = {}

log_file = "./scripts/import_recup_intervenants.log"
logging.basicConfig(filename=log_file,level=logging.DEBUG)

def parse_intervenant(data):
    services = []
    workers = []

    if data["old_cmpp_id"]:
        workers_qs = Worker.objects.filter(old_cmpp_id=data["old_cmpp_id"])
        if workers_qs:
            workers.extend(workers_qs.all())
        services.append(Service.objects.get(name="CMPP"))
    if data["old_camsp_id"]:
        workers_qs = Worker.objects.filter(old_camsp_id=data["old_camsp_id"])
        if workers_qs:
            workers.extend(workers_qs.all())
        services.append(Service.objects.get(name="CAMSP"))
    if data["old_sessad_ted_id"]:
        workers_qs = Worker.objects.filter(old_sessad_ted_id=data["old_sessad_ted_id"])
        if workers_qs:
            workers.extend(workers_qs.all())
        services.append(Service.objects.get(name="SESSAD TED"))
    if data["old_sessad_dys_id"]:
        workers_qs = Worker.objects.filter(old_sessad_dys_id=data["old_sessad_dys_id"])
        if workers_qs:
            workers.extend(workers_qs.all())
        services.append(Service.objects.get(name="SESSAD DYS"))
    events = Event.objects.filter(participants__in=workers)
    worker = Worker.objects.get(id=workers[0].id)
    worker.id = None
    worker.pk = None
    worker.last_name = data['nom']
    if data['prenom']:
        worker.first_name = data['prenom']
    worker_type = None
    if data['type readable'] == 'Stagiaire':
        worker_type = WorkerType.objects.get(name=u'Stagiaires', intervene=True)
    elif data['type readable'] == 'Orthophoniste liberal':
        worker_type = WorkerType.objects.get(name=u'Orthophonistes libéraux', intervene=True)
    worker.type = worker_type
    worker.save()
    if worker.type.name == u'Stagiaires':
        username="%s%s" % (worker.first_name[0].lower(), worker.last_name.lower())
        password = worker.first_name[0].lower() + worker.last_name.lower()
        user = User.objects.filter(username=username)
        if not user:
            for i in range(0, 4):
                password += str(random.randint(0, 9))
            user = User.objects.create_user(
                username=username,
                password=password,
                )
            user.first_name = worker.first_name
            user.last_name = worker.last_name
            user.save()
            UserWorker.objects.create(user=user, worker=worker)
            logging.info("Create user %s with password %s" % (username, password))
    worker.services = services
    if events and len(workers) > 1:
        for event in events:
            event.participants.add(worker)
            for old_worker in workers:
                event.participants.remove(old_worker)
    for old_worker in workers:
        logging.info('delete worker %s' % old_worker.id)
        old_worker.delete()
    logging.info('create worker %s' % worker.id)
    worker.save()

def main():
    csvfile = open('scripts/recup_intervenants.csv', 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    cols = csvlines.next()
    for line in csvlines:
        data = _get_dict(cols, line)
        parse_intervenant(data)
    csvfile.close()
#    tables_data = {}
#    for db in dbs:
#        if "F_ST_ETIENNE_CMPP" == db:
#            service = Service.objects.get(name="CMPP")
#        elif "F_ST_ETIENNE_CAMSP" == db:
#            service = Service.objects.get(name="CAMSP")
#        elif "F_ST_ETIENNE_SESSAD_TED" == db:
#            service = Service.objects.get(name="SESSAD TED")
#        elif "F_ST_ETIENNE_SESSAD" == db:
#            service = Service.objects.get(name="SESSAD DYS")
#
#        tables_data[service] = {}
#
#        for table in tables:
#            tables_data[service][table] = {}
#            csvfile = open(os.path.join(db_path, db, '%s.csv' % table), 'rb')
#            csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
#            cols = csvlines.next()
#            for line in csvlines:
#                data = _get_dict(cols, line)
#                tables_data[service][table][data['id']] = data
#            csvfile.close()
#

if __name__ == "__main__":
    main()

