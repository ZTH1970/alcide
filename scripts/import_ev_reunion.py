# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
"""


import os
import csv
import logging
from datetime import datetime, timedelta

import calebasse.settings
import django.core.management
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction

from calebasse.agenda.models import Event, EventType
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service

from scripts.import_rs import PERIOD_FAURE_NOUS

# Configuration
db_path = "./scripts/20121221-192258"
log_file = "./scripts/import_ev_reunion.log"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
tables = ['rs', 'ev', 'details_rs', 'details_ev']

# Global mappers. This dicts are used to map a Faure id with a calebasse object.
tables_data = {}

def _to_datetime(str_date):
    if not str_date:
        return None
    return datetime.strptime(str_date[:19], "%Y-%m-%d %H:%M:%S")

def _to_date(str_date):
    dt = _to_datetime(str_date)
    return dt and dt.date()

def _to_time(str_date):
    dt = _to_datetime(str_date)
    return dt and dt.time()

def _to_duration(str_date):
    dt = _to_datetime(str_date)
    if dt is None:
        return timedelta(minutes=15)
    return dt - datetime(1900, 01, 01, 0, 0)

def _get_dict(cols, line):
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res

def _get_therapists(line, table_name, service):
    p_ids = []
    for id, detail in tables_data['details_%s' % table_name].iteritems():
        if detail['%s_id' % table_name] == line['id']:
            p_ids.append(detail['thera_id'])
    participants = []
    for p_id in p_ids:
        try:
            if service.name == "CMPP":
                participants.append(Worker.objects.get(old_cmpp_id=int(p_id)))
            elif service.name == "CAMSP":
                participants.append(Worker.objects.get(old_camsp_id=int(p_id)))
            elif service.name == "SESSAD DYS":
                participants.append(Worker.objects.get(old_sessad_dys_id=int(p_id)))
            elif service.name == "SESSAD TED":
                participants.append(Worker.objects.get(old_sessad_ted_id=int(p_id)))
        except Worker.DoesNotExist:
            logging.warning("%s %s_id %s thera_id %s" %\
                    (service.name, table_name, line['id'], p_id) +\
                    " therapeute non trouve")

    return participants

def create_event(line, service, tables_data):
    if not Event.objects.filter(old_rs_id=line['id'], services__in=[service]):
        # Manage exception
        exception_date = None
        exception_to = None
        exception_error = False
        if line['rr_ev_id']:
            ev_id = int(line['rr_ev_id'][3:])
            exception_date = _to_date(line['date_rdv'])
            exception_to = Event.objects.filter(old_ev_id=ev_id,
                    services__in=[service])
            if exception_to:
                exception_to = exception_to[0]
                if Event.objects.filter(exception_date=exception_date,
                        exception_to=exception_to):
                    logging.info("rs_id %s is duplicated" % line["id"])
                    return
            else:
                exception_error = True
        event_type = EventType.objects.get(id=4)
        start_datetime = datetime.strptime(
                line['date_rdv'][:-13] + ' ' + line['heure'][11:-4],
                "%Y-%m-%d %H:%M:%S")
        end_datetime = start_datetime + timedelta(
                hours=int(line['duree'][11:-10]),
                minutes=int(line['duree'][14:-7]),
                )
        participants = _get_therapists(line, 'rs', service)
        if not exception_error:
            event = Event.objects.create(
                    title=line['libelle'][:60],
                    description=line['texte'],
                    event_type=event_type,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    old_rs_id=line['id'],
                    exception_to = exception_to,
                    exception_date = exception_date
                    )
            event.services = [service]
            event.participants = participants
            event.save()
        else:
            logging.error("%s rs_id %s exception pas d'ev trouve %s" % (service.name,
                line["id"], line))

def create_recurrent_event(line, service, tables_data):
    if not Event.objects.filter(old_ev_id=line['id'], services__in=[service]):
        start_date = _to_date(line['date_debut'])
        end_date = _to_date(line['date_fin'])
        if end_date and start_date > end_date:
            logging.warning('%s ev_id %s date_fin < date_debut' % \
                    (service.name, line['id']))
        time = _to_time(line['heure'])
        duration = _to_duration(line['duree'])
        start_datetime = datetime.combine(start_date, time)
        end_datetime = start_datetime + duration

        # connect rythme
        rythme = int(line['rythme'])
        if PERIOD_FAURE_NOUS.get(rythme):
            recurrence_periodicity = PERIOD_FAURE_NOUS[rythme]
        else:
            recurrence_periodicity = None
            logging.warning('%s ev_id %s rythme not found %s' % \
                    (service.name, line['id'], line['rythme']))

        participants = _get_therapists(line, 'ev', service)
        event_type = EventType.objects.get(id=4)
        try:
            event = Event.objects.create(
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                event_type=event_type,
                title=line['libelle'],
                old_ev_id=line['id'],
                description=line['note'],
                recurrence_periodicity=recurrence_periodicity,
                recurrence_end_date=end_date)
            event.services = [service]
            event.participants = participants
            event.save()
        except django.core.exceptions.ValidationError, e:
            logging.error(service.name + ' ev recurrence non valide %s %s' % (line, e))

@transaction.commit_on_success
def main():
    logging.basicConfig(filename=log_file,level=logging.DEBUG)
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
            csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
            cols = csvlines.next()
            tables_data[table] = {}
            for line in csvlines:
                data = _get_dict(cols, line)
                tables_data[table][data['id']] = data
            csvfile.close()

        for id, line in tables_data['ev'].iteritems():
            if line['libelle'].replace(u'é', u'e').upper() not in ('ARRIVEE', 'DEPART'):
                create_recurrent_event(line, service, tables_data)

        for id, line in tables_data['rs'].iteritems():
            if (not line['enfant_id'] or not int(line['enfant_id'])) \
                    and (line['libelle'].replace(u'é', u'e').upper() not in ('ARRIVEE', 'DEPART')):
                create_event(line, service, tables_data)

if __name__ == "__main__":
    main()

