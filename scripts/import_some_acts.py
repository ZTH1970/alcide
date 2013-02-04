# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv

from datetime import datetime, date

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction
from calebasse.dossiers.models import PatientRecord
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service
from calebasse.ressources.models import ActType
from calebasse.actes.models import Act, ActValidationState

from import_dossiers import map_cs

# Configuration
db_path = "./scripts/20130104-213225"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
# dbs = ["F_ST_ETIENNE_CAMSP"]

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

def batch_delete(qs, limit):
    count = qs.count()
    i = 0
    while i < count:
        ids = qs[i:i+limit].values_list('pk', flat=True)
        qs.filter(pk__in=ids).delete()
        i += limit


PERIOD_FAURE_NOUS = {1 : 1,
2 : 2,
3 : 3,
4 : 4,
5: 6,
6: 7,
7: 8,
8: 9,
9: None,
10: 10,
12: 11,
13: 12,
}

JOURS = {1: 'lundi',
2: 'mardi',
3: 'mercredi',
4: 'jeudi',
5: 'vendredi'
}

dic_worker = {}

def load_csv2(db, name, offset=0, limit=9999999, id_column=0):
    csvfile = open(os.path.join(db_path, db, name + '.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    cols = csvlines.next()
    yield cols
    i = 0
    for line in csvlines:
        if not (offset <= int(line[id_column]) < offset+limit):
            continue
        yield _get_dict(cols, line)
        i += 1
    csvfile.close()

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

log = open('import_some_acts-%s.log' % datetime.now().isoformat(), 'w+')

@transaction.commit_on_success
def main():
    """ """

    workers = Worker.objects.all()
    for db in dbs:
        workers_idx = {}
        act_types_idx = {}
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
        print >>log, datetime.now(), '===', service.name, '==='

        # load workers mapping
        worker_reverse_idx = {}
        for i, worker in enumerate(workers):
            if service.name == 'CMPP':
                j = worker.old_cmpp_id
            elif service.name == 'CAMSP':
                j = worker.old_camsp_id
            elif service.name == 'SESSAD DYS':
                j = worker.old_sessad_dys_id
            elif service.name == 'SESSAD TED':
                j = worker.old_sessad_ted_id
            else:
                print "service inconnu!!!"
                exit(0)
            if j:
                workers_idx[j] = worker
                worker_reverse_idx[worker] = j
        # load act_type mapping
        act_types = ActType.objects.for_service(service)
        act_type_id_not_found = set()
        for i, act_type in enumerate(act_types):
            j = act_type.old_id
            if j:
                act_types_idx[j] = act_type
            else:
                act_type_id_not_found.add(act_type)

        def set_act_type(row, not_found=None):
            act_type_id = row['type_acte']
            if act_type_id == '0':
                add_invalid(row, 'no act_id=>not importable')
            elif act_type_id in act_types_idx:
                row['act_type'] = act_types_idx[act_type_id]
            else:
                add_invalid(row, 'act_type not found %s' % act_type_id)
                if not_found:
                    not_found.add(act_type_id)

        def handle_details2(data, idx, details, id_key):
            for detail in details:
                i = int(detail[id_key])
                thera_id = detail['thera_id']
                if i not in idx:
                    continue
                row = data[idx[i]]
                if thera_id in workers_idx:
                    ws = row.setdefault('workers', set())
                    theras = row.setdefault('theras', set())
                    ws.add(workers_idx[thera_id])
                    theras.add(thera_id)
                else:
                    add_invalid(row, 'unknown thera_id %s' % thera_id)

        print "%s - Nombre de types d'actes : %d" % (service.name, len(act_types))
        print "%s - Liste des types d'actes sans id : %s" % (service.name, str(act_type_id_not_found))

        # loading dossiers idx
        enfant_idx = {}
        for enfant in PatientRecord.objects.filter(service=service):
            enfant_idx[enfant.old_id] = enfant

        def set_enfant(row, not_found=None):
            # connect enfant
            enfant_id = row['enfant_id']
            if enfant_id == '0':
                add_invalid(row, 'no enfant_id=>not an appointment')
                row['event'] = True
            elif enfant_id in enfant_idx:
                row['enfant'] = enfant_idx[enfant_id]
            else:
                add_invalid(row, 'enfant_id not found %s' % enfant_id)
                if not_found:
                    not_found.add(enfant_id)

        acts_ids = set([
                    193815,
                    173334,
                    171872,
                    193506,
                    182039,
                    166806,
                    183054,
                    181050,
                    172301,
                    193914,
                    186876,
                    161111,
                   ])

        rows = load_csv2(db, 'actes')
        rows.next()
        loaded_rows = []
        for row in rows:
            if int(row['id']) not in acts_ids:
                continue
            row.setdefault('invalid', '')
            row.setdefault('workers', set())
            row.setdefault('theras', set())
            row['date'] = _to_date(row['date_acte'])
            row['time'] = _to_time(row['heure'])
            row['duration'] = _to_duration(row['duree'])
            row['is_billed'] = row['marque'] == '1'
            row['validation_locked'] = row['date'] < date(2013, 1, 3)
            set_enfant(row)
            set_act_type(row)
            row['state'] = map_cs[service.name].get(row['cs'], 'VALIDE')
            loaded_rows.append(row)
        total = 0
        for row in loaded_rows:
            if row['invalid']:
                print >>log, datetime.now(), 'row invalid', row
                continue
            print >>log, datetime.now(), 'act', row['id'], 'imported'
#            act = Act.objects.create(
#                    old_id=row['id'],
#                    date=row['date'],
#                    time=row['time'],
#                    _duration=row['duration'].seconds // 60,
#                    is_billed=row['is_billed'],
#                    act_type=row['act_type'],
#                    patient=row['enfant'],
#                    validation_locked=row['validation_locked'])
#            act.doctors = row['workers']
#            ActValidationState.objects.create(act=act, state_name=row['state'], previous_state=None)
            total += 1
        print >>log, datetime.now(), 'created', total, 'new acts'
    raise Exception()

if __name__ == "__main__":
    main()
