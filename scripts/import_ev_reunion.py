# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Import reunion and 
"""


import os
import csv
import logging
from datetime import datetime, timedelta

import calebasse.settings
import django.core.management
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

django.core.management.setup_environ(calebasse.settings)


from calebasse.agenda.models import Event, EventType
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service

# Configuration
db_path = "./scripts/20121221-192258"
log_file = "./scripts/import_ev_reunion.log"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
tables = ['rs', 'ev', 'details_rs', 'details_ev']

# Global mappers. This dicts are used to map a Faure id with a calebasse object.
tables_data = {}

def _get_dict(cols, line):
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res

def create_event(line, service, tables_data):
    if not Event.objects.filter(old_ev_id=line['id']):
        event_type = EventType.objects.get(id=4)
        start_datetime = datetime.strptime(
                line['date_rdv'][:-13] + ' ' + line['heure'][11:-4],
                "%Y-%m-%d %H:%M:%S")
        end_datetime = start_datetime + timedelta(
                hours=int(line['duree'][11:-10]),
                minutes=int(line['duree'][14:-7]),
                )
        # Find therapists
        p_ids = []
        for id, detail_rs in tables_data['details_rs'].iteritems():
            if detail_rs['rs_id'] == line['id']:
                p_ids.append(detail_rs['thera_id'])
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
                logging.warning("rs_id %s thera_id %s" % (line['id'], p_id)  + " therapeute non trouve " +  service.name)

        event = Event.objects.create(
                title=line['libelle'][:60],
                description=line['texte'],
                event_type=event_type,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                old_ev_id=line['id'],
                )
        event.services = [service]
        event.participants = participants
        event.save()

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

        for id, line in tables_data['rs'].iteritems():
            if not line['enfant_id'] or not int(line['enfant_id']):
                if not line['rr_ev_id']:
                    create_event(line, service, tables_data)

        for id, line in tables_data['ev'].iteritems():
            if line['libelle'].upper() not in ('ARRIVEE', 'DEPART'):
                pass

if __name__ == "__main__":
    main()

