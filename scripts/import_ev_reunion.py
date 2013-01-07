# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
"""


import os
import csv
import logging
from datetime import datetime, timedelta

log_file = "./scripts/import_ev_reunion.log"
logging.basicConfig(filename=log_file,level=logging.DEBUG)

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction

from calebasse.agenda.models import Event, EventType
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service

from scripts.import_rs import PERIOD_FAURE_NOUS

# Configuration
db_path = "./scripts/20121221-192258"

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

import utils

worker_indexes = utils.QuerysetIndex(Worker.objects.all(),
        'old_cmpp_id', 'old_camsp_id', 'old_sessad_dys_id', 'old_sessad_ted_id')

def _get_therapists(line, table_name, service):
    global worker_indexes
    p_ids = []
    for id, detail in tables_data['details_%s' % table_name].iteritems():
        if detail['%s_id' % table_name] == line['id']:
            p_ids.append(detail['thera_id'])
    participants = []
    for p_id in p_ids:
        try:
            if service.name == "CMPP":
                worker = worker_indexes.by_old_cmpp_id[p_id]
            elif service.name == "CAMSP":
                worker = worker_indexes.by_old_camsp_id[p_id]
            elif service.name == "SESSAD DYS":
                worker = worker_indexes.by_old_sessad_dys_id[p_id]
            elif service.name == "SESSAD TED":
                worker = worker_indexes.by_old_sessad_ted_id[p_id]
            participants.append(worker)
        except KeyError:
            logging.warning("%s %s_id %s thera_id %s" %\
                    (service.name, table_name, line['id'], p_id) +\
                    " therapeute non trouve")

    return participants

def _is_timetable(line):
    return line and line['libelle'].replace(u'é', u'e').upper() in ('ARRIVEE', 'DEPART')

def _get_ev(tables, line):
    ev_id = line['rr_ev_id']
    if not ev_id or not ev_id.startswith('ev_'):
        return None
    return tables['ev'].get(ev_id[3:])

ServicesThrough = Event.services.through
ParticipantsThrough = Event.participants.through

event_type_4 = EventType.objects.get(id=4)

def create_event(line, service, tables_data, rs_by_id, events_by_id, events,
        participants_by_id, exceptions_set):
    if line['id'] in rs_by_id:
        logging.warning("%s rs %s already loaded", service.name, line['id'])
        return
    # Manage exception
    exception_date = None
    exception_to = None
    exception_error = False
    if line['rr_ev_id']:
        assert line['rr_ev_id'].startswith('ev_')
        ev_id = int(line['rr_ev_id'][3:])
        exception_date = _to_date(line['date_rdv'])
        exception_to = events_by_id.get(str(ev_id))
        if exception_to:
            p = (exception_date, exception_to)
            if p in exceptions_set:
                logging.info("rs_id %s is duplicated" % line["id"])
                return
            exceptions_set.add(p)
        else:
            exception_error = True
    start_datetime = datetime.strptime(
            line['date_rdv'][:-13] + ' ' + line['heure'][11:-4],
            "%Y-%m-%d %H:%M:%S")
    end_datetime = start_datetime + timedelta(
            hours=int(line['duree'][11:-10]),
            minutes=int(line['duree'][14:-7]),
            )
    participants = _get_therapists(line, 'rs', service)
    if not participants:
        logging.error("%s rs_id %s exception aucun participant importable" % (service.name,
            line["id"]))
        return
    if not exception_error:
        event = Event(
                title=line['libelle'][:60],
                description=line['texte'],
                event_type=event_type_4,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                old_rs_id=line['id'],
                exception_to = Event(id=exception_to),
                exception_date = exception_date
                )
        participants_by_id[line['id']] = participants
        events.append(event)
    else:
        logging.error("%s rs_id %s exception pas d'ev trouve %s" % (service.name,
            line["id"], line))

def create_recurrent_event(line, service, tables_data, events, participants_by_id):
    if Event.objects.filter(old_ev_id=line['id'], services__in=[service]):
        logging.warning("%s ev %s already loaded", service.name, line['id'])
        return
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
    if not participants:
        logging.error("%s ev_id %s exception aucun participant importable" % (service.name,
            line["id"]))
        return
    try:
        event = Event(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            event_type=event_type_4,
            title=line['libelle'],
            old_ev_id=line['id'],
            description=line['note'],
            recurrence_periodicity=recurrence_periodicity,
            recurrence_end_date=end_date)
        participants_by_id[line['id']] = participants
        events.append(event)
    except django.core.exceptions.ValidationError, e:
        logging.error(service.name + ' ev recurrence non valide %s %s' % (line, e))

@transaction.commit_on_success
def main():
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

        total = 0
        events = []
        participants = dict()
        for id, line in tables_data['ev'].iteritems():
            if not _is_timetable(line):
                total += 1
                create_recurrent_event(line, service, tables_data, events,
                        participants)

        # create events
        logging.info('%s creating %s events on %s',
                service.name, len(events), total)
        Event.objects.bulk_create(events)
        participants_through = []
        # get their ids
        events_by_id = dict(Event.objects \
                .exclude(event_type_id=1) \
                .filter(services__isnull=True, old_ev_id__isnull=False) \
                .values_list('old_ev_id', 'id'))
        for line_id, participants in participants.iteritems():
            for participant in participants:
                pt = ParticipantsThrough(event_id=events_by_id[line_id],
                        people_id=participant.people_ptr_id)
                participants_through.append(pt)
        ParticipantsThrough.objects.bulk_create(participants_through)
        ServicesThrough.objects.bulk_create([
            ServicesThrough(service_id=service.id, event_id=event_id) for event_id in events_by_id.values()])
        participants = {}

        total = 0
        events = []
        participants = dict()
        exceptions_set = set()
        # get their ids
        rs_by_id = dict(Event.objects \
                .exclude(event_type_id=1) \
                .filter(services=service, old_rs_id__isnull=False) \
                .values_list('old_rs_id', 'id'))
        for id, line in tables_data['rs'].iteritems():
            if (not line['enfant_id'] or not int(line['enfant_id'])) \
                    and not _is_timetable(line) \
                    and (not _is_timetable(_get_ev(tables_data, line))):
                total += 1
                create_event(line, service, tables_data, rs_by_id, events_by_id,
                        events, participants, exceptions_set)
        # create events
        logging.info('%s creating %s events on %s',
                service.name, len(events), total)
        Event.objects.bulk_create(events)
        participants_through = []
        # get their ids
        events_by_id = dict(Event.objects \
                .exclude(event_type_id=1) \
                .filter(services__isnull=True, old_rs_id__isnull=False) \
                .values_list('old_rs_id', 'id'))
        for line_id, participants in participants.iteritems():
            for participant in participants:
                pt = ParticipantsThrough(event_id=events_by_id[line_id],
                        people_id=participant.people_ptr_id)
                participants_through.append(pt)
        ParticipantsThrough.objects.bulk_create(participants_through)
        logging.info('%s created %s participants links', service.name, len(participants_through))
        ServicesThrough.objects.bulk_create([
            ServicesThrough(service_id=service.id, event_id=event_id) for event_id in events_by_id.values()])
        participants = {}


if __name__ == "__main__":
    main()

