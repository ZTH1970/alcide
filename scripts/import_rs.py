# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv

from datetime import datetime, time, date

import calebasse.settings
import django.core.management
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

django.core.management.setup_environ(calebasse.settings)

from django.contrib.auth.models import User

from calebasse.agenda.models import Event, EventType
from calebasse.dossiers.models import PatientRecord, Status, FileState
from calebasse.ressources.models import Service
from calebasse.personnes.models import Worker, Holiday, TimeTable, PERIODICITIES
from calebasse.personnes.forms import PERIOD_LIST_TO_FIELDS
from calebasse.ressources.models import WorkerType, HolidayType, ActType

# Configuration
db_path = "./scripts/20121221-192258"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]

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

def load_csv(db, name):
    records = []
    idx = {}

    csvfile = open(os.path.join(db_path, db, name + '.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    cols = csvlines.next()
    i = 0
    for line in csvlines:
        # ignore line for timetable
        data = _get_dict(cols, line)
        records.append(data)
        idx[data['id']] = i
        i += 1
    csvfile.close()
    return records, idx, cols

def main():
    """ """

    workers = Worker.objects.all()
    invalid_rs_csv = open('./scripts/invalid.csv', 'wb+')
    writer = csv.writer(invalid_rs_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for db in dbs:
        workers_idx = {}
        act_types_idx = {}
        not_found = set()
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

        rs_data, rs_idx, rs_cols = load_csv(db, 'rs')
        rr_data, rr_idx, rr_cols = load_csv(db, 'rr')
        writer.writerow(map(lambda x: x.encode('utf-8'), rs_cols))

        print "%s - Nombre de rdv : %d" % (service.name, len(rs_data))
        print u"%s - Nombre de rdv récurrents : %d" % (service.name, len(rr_data))

        rs_details_data, _, _ = load_csv(db, 'details_rs')
        rr_details_data, _, _ = load_csv(db, 'details_rr')
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

        act_types = ActType.objects.for_service(service)
        act_type_id_not_found = set()
        for i, act_type in enumerate(act_types):
            j = act_type.old_id
            if j:
                act_types_idx[j] = act_type
            else:
                act_type_id_not_found.add(act_type)

        not_found = set()
        rs_not_found = set()
        for rs_detail in rs_details_data:
            rs_id = rs_detail['rs_id']
            thera_id = rs_detail['thera_id']
            if rs_id not in rs_idx:
                rs_not_found.add(rs_id)
                continue
            rs = rs_data[rs_idx[rs_id]]
            if thera_id in workers_idx:
                rs_workers = rs.setdefault('workers', set())
                rs_workers.add(workers_idx[thera_id])
            else:
                rs['valid'] = False
                not_found.add(thera_id)


        print "%s - Liste des worker not found : %s" % (service.name, str(set(not_found)))
        print "%s - Liste des details pour des RS not found : %s" % (service.name, str(set(rs_not_found)))

        print "%s - Nombre de types d'actes : %d" % (service.name, len(act_types))
        print "%s - Liste des types d'actes sans id : %s" % (service.name, str(act_type_id_not_found))

        enfant_idx = {}
        for enfant in PatientRecord.objects.filter(service=service):
            enfant_idx[enfant.old_id] = enfant

        enfant_not_found = set()
        rr_not_found = set()
        rs_without_act_type = set()
        unknown_act_type_id = set()
        invalid_rs = set()
        for rs in rs_data:
            rs['ok'] = True
            rs.setdefault('valid', True)
            # connect enfant
            enfant_id = rs['enfant_id']
            if enfant_id == '0':
                rs['ok'] = False
            elif enfant_id in enfant_idx:
                rs['enfant'] = enfant_idx[enfant_id]
            else:
                rs['ok'] = rs['valid'] = False
                enfant_not_found.add(enfant_id)
            # connect rr
            rr_id = rs['rr_ev_id']
            if rr_id:
                if rr_id.startswith('ev_'):
                    rs['ok'] = False
                elif rr_id.startswith('rr_'):
                    _, rr_id = rr_id.split('_')
                    if rr_id in rr_idx:
                        rs['rr'] = rr_data[rr_idx[rr_id]]
                    else:
                        rs['ok'] = False
                        rr_not_found.add(rr_id)
                else:
                    print 'invalid rr_id', rr_id
            rs['date_rdv'] = _to_date(rs['date_rdv'])
            rs['heure'] = _to_time(rs['heure'])
            rs['duree'] = _to_duration(rs['duree'])
            act_type_id = rs['type_acte']
            if act_type_id == '0' and rs['enfant_id'] == '0':
                rs['ok'] = False
            elif act_type_id:
                if act_type_id in act_types_idx:
                    rs['act_type'] = act_types_idx[act_type_id]
                else:
                    rs['ok'] = rs['valid'] = False
                    unknown_act_type_id.add(act_type_id)
            else:
                raise NotImplemented
            if not rs['valid']:
                invalid_rs.add(rs['id'])
                writer.writerow([ unicode(rs[col]).encode('utf-8') for col in rs_cols ])


        print "%s - Liste des enfants not found : %s" % (service.name, str(enfant_not_found))
        print "%s - Liste des RR not found : %s" % (service.name, str(rr_not_found))
        print "%s - Liste des RS sans type d'acte : %s" % (service.name, str(rs_without_act_type))
        print "%s - Liste des types d'actes inconnus : %s" % (service.name, str(unknown_act_type_id))
        print "%s - Liste des RS invalides : %s" % (service.name, len(invalid_rs))

    invalid_rs_csv.close()

if __name__ == "__main__":
    main()
