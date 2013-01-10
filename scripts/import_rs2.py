# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv

from datetime import datetime, date

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction
from calebasse.agenda.models import EventWithAct
from calebasse.dossiers.models import PatientRecord
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service
from calebasse.ressources.models import ActType
from calebasse.actes.models import Act, ActValidationState

from import_dossiers import map_cs

# Configuration
db_path = "./scripts/20130104-213225"

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

def load_csv(db, name, offset=0, limit=9999999, id_column=0, year=None):
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
        if year and not (('date_rdv' in data and data['date_rdv'].startswith(str(year))) \
                or ('date_debut' in data and data['date_debut'].startswith(str(year)))):
            continue
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
        print "%s - Nombre de types d'actes : %d" % (service.name, len(act_types))
        print "%s - Liste des types d'actes sans id : %s" % (service.name, str(act_type_id_not_found))

        invalid_rs = set()
        invalid_rr = set()
        new_rs = []
        new_rr = []
        invalid_rs_csv = open('./scripts/invalid_rs_%s.csv' % (service.name, ), 'wb+')
        invalid_rs_writer = csv.writer(invalid_rs_csv, delimiter=',',
                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        invalid_rr_csv = open('./scripts/invalid_rr_%s.csv' % (service.name, ), 'wb+')
        invalid_rr_writer = csv.writer(invalid_rr_csv, delimiter=',',
                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for year in range(2011, 2014):
            print service.name, ' - Year', year
            rs_data, rs_idx, rs_cols = load_csv(db, 'rs', year=year)
            rr_data, rr_idx, rr_cols = load_csv(db, 'rr', year=year)
            print service.name, year, 'read', len(rs_data), 'rs and', len(rr_data), 'rr'
            rs_cols.extend(['workers', 'invalid'])
            rr_cols.extend(['workers', 'invalid'])
            invalid_rs_writer.writerow(map(lambda x: x.encode('utf-8'), rs_cols))
            invalid_rr_writer.writerow(map(lambda x: x.encode('utf-8'), rr_cols))

            single_rdv_idx = dict(EventWithAct.objects.filter(services=service,
                    start_datetime__year=year,
                    recurrence_periodicity__isnull=True).values_list('old_rs_id', 'id'))
            multi_rdv_idx = dict(EventWithAct.objects.filter(services=service,
                    start_datetime__year=year,
                    recurrence_periodicity__isnull=False).values_list('old_rr_id', 'id'))

            rs_details_data, _, _ = load_csv(db, 'details_rs')
            rr_details_data, _, _ = load_csv(db, 'details_rr')

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

            def handle_details(data, idx, details, id_key):
                not_found = set()
                for detail in details:
                    i = detail[id_key]
                    thera_id = detail['thera_id']
                    if i not in idx:
                        continue
                    row = data[idx[i]]
                    if thera_id in workers_idx:
                        workers = row.setdefault('workers', set())
                        workers.add(workers_idx[thera_id])
                    else:
                        # add_invalid(row, 'unknown thera_id %s' % thera_id)
                        not_found.add(thera_id)
                print "%s - Liste des worker not found : %s" % (service.name, str(set(not_found)))

            print ' - Traitement rs_detail....'
            handle_details(rs_data, rs_idx, rs_details_data, 'rs_id')
            print ' - Traitement rr_detail....'
            handle_details(rr_data, rr_idx, rr_details_data, 'rr_id')

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

            enfant_not_found = set()
            rr_not_found = set()
            rs_without_act_type = set()
            unknown_act_type_id = set()
            for rs in rs_data:
                if rs['id'] in single_rdv_idx:
                    continue
                rs.setdefault('workers', set())
                rs['exception'] = False
                rs['event'] = False
                rs['date'] = _to_date(rs['date_rdv'])
                # connect enfant
                set_enfant(rs)
                set_act_type(rs)
                if rs['event']:
                    continue
                # connect rr
                rr_id = rs['rr_ev_id']
                if rr_id:
                    if rr_id.startswith('ev_'):
                        continue
                rs['time'] = _to_time(rs['heure'])
                rs['duration'] = _to_duration(rs['duree'])
                rs['start_datetime'] = datetime.combine(rs['date'], rs['time'])
                rs['end_datetime'] = rs['start_datetime'] + rs['duration']
                if len(rs['workers']) == 0:
                    add_invalid(rs, 'aucun participant')
                if rs.get('invalid') and not rs['event']:
                    invalid_rs.add(rs['id'])
                    invalid_rs_writer.writerow([ unicode(rs[col]).encode('utf-8') for col in rs_cols ])
                else:
                    new_rs.append(rs)


            print "%s - Liste des enfants not found : %s" % (service.name, str(enfant_not_found))
            print "%s - Liste des RR not found : %s" % (service.name, str(rr_not_found))
            print "%s - Liste des RS sans type d'acte : %s" % (service.name, str(rs_without_act_type))
            print "%s - Liste des types d'actes inconnus : %s" % (service.name, str(unknown_act_type_id))
            print

            enfant_not_found = set()
            rr_not_found = set()
            rs_without_act_type = set()
            unknown_act_type_id = set()
            for rr in rr_data:
                if rr['id'] in multi_rdv_idx:
                    continue
                rr['event'] = False
                rs.setdefault('workers', set())
                rr.setdefault('exceptions', [])
                rr['start_date'] = _to_date(rr['date_debut'])
                rr['end_date'] = _to_date(rr['date_fin'])
                if rr['end_date'] and rr['start_date'] > rr['end_date']:
                    add_invalid(rr, 'date_fin < date_debut')
                rr['time'] = _to_time(rr['heure'])
                rr['duration'] = _to_duration(rr['duree'])
                rr['start_datetime'] = datetime.combine(rr['start_date'], rr['time'])
                rr['end_datetime'] = rr['start_datetime'] + rr['duration']
                # connect rythme
                rr['rythme'] = int(rr['rythme'])
                if PERIOD_FAURE_NOUS.get(rr['rythme']):
                    rr['recurrence_periodicity'] = PERIOD_FAURE_NOUS[rr['rythme']]
                else:
                    add_invalid(rr, 'rythme not found %s' % rr['rythme'])
                set_enfant(rr)
                set_act_type(rr)
                if rr['event']:
                    continue
                if len(rr['workers']) == 0:
                    add_invalid(rr, 'aucun participant')
                if rr.get('invalid'):
                    invalid_rr.add(rr['id'])
                    invalid_rr_writer.writerow([ unicode(rr[col]).encode('utf-8') for col in rr_cols ])
                else:
                    new_rr.append(rr)
        print service.name, 'found', len(new_rs), 'individual rdv not imported'
        print service.name, 'found', len(invalid_rs), 'individual rdv invalid'
        print service.name, 'found', len(new_rr), 'multiple rdv not imported'
        print service.name, 'found', len(invalid_rr), 'multiple rdv invalid'

        for row in new_rs:
            act_id = row['base_id']
            if act_id == '0':
                continue
            acts = Act.objects.filter(old_id=act_id)
            row['act'] = None
            if len(acts) == 0:
                print service.name, 'act not imported', act_id, 'linked to rs', row['id']
            elif len(acts) > 1:
                print service.name, 'more than one act', acts.values_list('id', flat=True), 'linked to rs', row['id']
            else:
                row['act'] = acts[0]


        # RR
        for row in new_rr:
            event = EventWithAct.objects.create(
                    patient=row['enfant'],
                    start_datetime=row['start_datetime'],
                    end_datetime=row['end_datetime'],
                    act_type=row['act_type'],
                    old_rr_id=row['id'],
                    title=row['enfant'].display_name,
                    description=row['texte'],
                    recurrence_periodicity=row['recurrence_periodicity'],
                    recurrence_end_date=row['end_date'])
            event.services = [ service ]
            event.participants = row['workers']
            print 'created', event
        for row in new_rs:
            if row['exception'] or row.get('invalid'):
                continue
            exception_to = None
            exception_date = None
            if row['rr_ev_id']:
                _, rr_id = row['rr_ev_id'].split('_')
                e = EventWithAct.objects.filter(old_rr_id=rr_id)
                if len(e) == 0:
                    pass
                elif len(e) > 1:
                    add_invalid(row, 'more than one recurring event %s' % e.values_list('id', flat=True))
                    invalid_rs_writer.writerow([ unicode(row[col]).encode('utf-8') for col in rs_cols ])
                    continue
                else:
                    exception_to = e[0]
                    exception_date = row['start_datetime'].date()
            if exception_to and EventWithAct.objects.filter(exception_to=exception_to, exception_date=exception_date):
                print 'exception existante', EventWithAct.objects.filter(exception_to=exception_to, exception_date=exception_date), ' ligne ', row, 'ignore'
                continue


            event = EventWithAct.objects.create(patient=row['enfant'],
                    start_datetime=row['start_datetime'],
                    end_datetime=row['end_datetime'],
                    act_type=row['act_type'],
                    old_rs_id=row['id'],
                    title=row['enfant'].display_name,
                    description=row['texte'],
                    exception_to=exception_to,
                    exception_date=exception_date)
            event.services = [ service ]
            event.participants = row['workers']
            print 'created', event


if __name__ == "__main__":
    main()
