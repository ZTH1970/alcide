# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Import reunion and 
"""

import os
import csv

from datetime import datetime, timedelta

import calebasse.settings
import django.core.management
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

django.core.management.setup_environ(calebasse.settings)


from calebasse.agenda.models import Event, EventType
from calebasse.ressources.models import Service

# Configuration
db_path = "./scripts/20121221-192258"

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
        date_debut, heure, duree
        start_datetime = datetime.strptime(
                line['date_debut'][:-13] + ' ' + line['heure'][11:-4],
                "%Y-%m-%d %H:%M:%S")
        end_datetime = start_datetime + timedelta(
                hours=int(secondsline['duree'][11:-10]),
                minutes=int(secondsline['duree'][14:-7]),
                )
        # TODO: add pariticipants
        event = Event.objects.create(
                title=line['libelle'],
                description=line['texte'],
                event_type=event_type,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                #participants=,
                old_ev_id=line["id"],
                )

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

        for id, line in tables_data['rs'].iteritems():
            if not line['enfant_id'] or not int(line['enfant_id']):
                if not line['rr_ev_id']:
                    create_event(line, service, tables_data)

        for id, line in tables_data['ev'].iteritems():
            if line['libelle'].upper() not in ('ARRIVEE', 'DEPART'):
                print line
                #print line['rythme']

if __name__ == "__main__":
    main()

