# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv

from datetime import datetime

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction
from calebasse.agenda.models import Event
from calebasse.ressources.models import Service

import utils

# Configuration
db_path = "./scripts/20121221-192258"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
# dbs = ["F_ST_ETIENNE_SESSAD_TED"]

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
        return None
    return dt - datetime(1900, 01, 01, 0, 0)

def _to_int(str_int):
    if not str_int:
        return None
    return int(str_int)

def _get_dict(cols, line):
    """"""
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res

def load_csv(db, name, offset=0, limit=9999999, id_column=0):
    records = []
    idx = {}

    csvfile = open(os.path.join(db_path, db, name + '.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    cols = csvlines.next()
    i = 0
    for line in csvlines:
        if not (offset <= int(line[id_column]) < offset+limit):
            continue
        data = _get_dict(cols, line)
        records.append(data)
        idx[data['id']] = i
        i += 1
    csvfile.close()
    return records, idx, cols

def add_invalid(d, reason):
    d.setdefault('invalid', '')
    if d['invalid']:
        d['invalid'] += ', '
    d['invalid'] += reason

@transaction.commit_on_success
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

        print '===', service.name, '==='
        print datetime.now()
        limit = 20000

        event_indexes = utils.QuerysetIndex(
                Event.objects.filter(services=service),
                'old_rs_id')


        offset = 0
        while True:
            rs_data, rs_idx, rs_cols = load_csv(db, 'rs', offset=offset,
                    limit=limit)
            if not rs_data:
                break
            print 'Loading cancellation flag for', len(rs_data), 'events'
            events_id_to_cancel = []
            for line in rs_data:
                if line['id'] not in event_indexes.by_old_rs_id:
                    continue
                if line['desactivate'] == '-1':
                    event_id = event_indexes.by_old_rs_id[line['id']].id
                    events_id_to_cancel.append(event_id)
            print 'Updating', len(events_id_to_cancel), 'flags'
            Event.objects.filter(id__in=events_id_to_cancel) \
                    .update(canceled=True)
            offset += limit


if __name__ == "__main__":
    main()
