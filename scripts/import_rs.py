# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv

from datetime import datetime, date

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction
from calebasse.agenda.models import EventWithAct, Event
from calebasse.dossiers.models import PatientRecord
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service, Room
from calebasse.ressources.models import ActType
from calebasse.actes.models import Act

from import_dossiers import map_cs

# Configuration
db_path = "./scripts/20121221-192258"

# dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
dbs = ["F_ST_ETIENNE_SESSAD_TED"]

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

def add_invalid(d, reason):
    d.setdefault('invalid', '')
    if d['invalid']:
        d['invalid'] += ', '
    d['invalid'] += reason

def main():
    """ """

    workers = Worker.objects.all()
    invalid_rs_csv = open('./scripts/invalid_rs.csv', 'wb+')
    invalid_rs_writer = csv.writer(invalid_rs_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    invalid_rr_csv = open('./scripts/invalid_rr.csv', 'wb+')
    invalid_rr_writer = csv.writer(invalid_rr_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
        rs_cols.extend(['workers', 'invalid'])
        rr_cols.extend(['workers', 'invalid'])
        invalid_rs_writer.writerow(map(lambda x: x.encode('utf-8'), rs_cols))
        invalid_rr_writer.writerow(map(lambda x: x.encode('utf-8'), rr_cols))

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

        def set_act_type(row, not_found=None):
            act_type_id = row['type_acte']
            if act_type_id == '0' and row['enfant_id'] == '0':
                add_invalid(row, 'no act_id=>not an appointment')
                row['event'] = True
            elif act_type_id != '0':
                if act_type_id in act_types_idx:
                    row['act_type'] = act_types_idx[act_type_id]
                else:
                    add_invalid(row, 'act_type not found %s' % act_type_id)
                    if not_found:
                        not_found.add(act_type_id)
            else:
                raise NotImplemented

        def handle_details(data, idx, details, id_key):
            not_found = set()
            id_not_found = set()
            for detail in details:
                i = detail[id_key]
                thera_id = detail['thera_id']
                if i not in idx:
                    id_not_found.add(i)
                    continue
                row = data[idx[i]]
                if thera_id in workers_idx:
                    workers = row.setdefault('workers', set())
                    workers.add(workers_idx[thera_id])
                else:
                    add_invalid(row, 'unknown thera_id %s' % thera_id)
                    not_found.add(thera_id)

            print "%s - Liste des worker not found : %s" % (service.name, str(set(not_found)))
            print "%s - Liste des details pour des RS/RR not found : %s" % (service.name, str(set(id_not_found)))

        print ' - Traitement rs_detail....'
        handle_details(rs_data, rs_idx, rs_details_data, 'rs_id')
        print ' - Traitement rr_detail....'
        handle_details(rr_data, rr_idx, rr_details_data, 'rr_id')
        print "%s - Nombre de types d'actes : %d" % (service.name, len(act_types))
        print "%s - Liste des types d'actes sans id : %s" % (service.name, str(act_type_id_not_found))

        enfant_idx = {}
        for enfant in PatientRecord.objects.filter(service=service):
            enfant_idx[enfant.old_id] = enfant

        def set_enfant(row, not_found=None):
            # connect enfant
            enfant_id = row['enfant_id']
            if enfant_id == '0':
                add_invalid(row, 'not an appointment')
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
        invalid_rs = set()
        seen_exceptions = dict()
        for rs in rs_data:
            rs.setdefault('workers', set())
            rs['exception'] = False
            rs['event'] = False
            rs['date'] = _to_date(rs['date_rdv'])
            # connect enfant
            enfant_id = rs['enfant_id']
            if enfant_id == '0':
                add_invalid(rs, 'no enfant_id=>not an appointment')
                rs['event'] = True
            elif enfant_id in enfant_idx:
                rs['enfant'] = enfant_idx[enfant_id]
            else:
                add_invalid(rs, 'enfant_id not found %s' % enfant_id)
                enfant_not_found.add(enfant_id)
            # connect rr
            rr_id = rs['rr_ev_id']
            if rr_id:
                if rr_id.startswith('ev_'):
                    rs['ok'] = False
                elif rr_id.startswith('rr_'):
                    _, rr_id = rr_id.split('_')
                    if rr_id in rr_idx:
                        if (rr_id, rs['date']) not in seen_exceptions:
                            seen_exceptions[(rr_id, rs['date'])] = rs['id']
                            exceptions = rr_data[rr_idx[rr_id]].setdefault('exceptions', [])
                            exceptions.append(rs)
                            rs['exception'] = True
                        else:
                            add_invalid(rs, 'already another exception on the same day: %s' %
                                    seen_exceptions[(rr_id, rs['date'])])
                    else:
                        add_invalid(rs, 'rr_id not found %s' % rr_id)
                        rr_not_found.add(rr_id)
                else:
                    add_invalid(rs, 'rr_id invalid %s' % rr_id)
            rs['time'] = _to_time(rs['heure'])
            rs['duration'] = _to_duration(rs['duree'])
            rs['start_datetime'] = datetime.combine(rs['date'], rs['time'])
            rs['end_datetime'] = rs['start_datetime'] + rs['duration']
            act_type_id = rs['type_acte']
            if act_type_id == '0' and rs['enfant_id'] == '0':
                add_invalid(rs, 'no act_id=>not an appointment')
                rs['event'] = True
            elif act_type_id:
                if act_type_id in act_types_idx:
                    rs['act_type'] = act_types_idx[act_type_id]
                else:
                    add_invalid(rs, 'act_type not found %s' % act_type_id)
                    unknown_act_type_id.add(act_type_id)
            else:
                raise NotImplemented
            if rs.get('invalid') and not rs['event']:
                invalid_rs.add(rs['id'])
                invalid_rs_writer.writerow([ unicode(rs[col]).encode('utf-8') for col in rs_cols ])


        print "%s - Liste des enfants not found : %s" % (service.name, str(enfant_not_found))
        print "%s - Liste des RR not found : %s" % (service.name, str(rr_not_found))
        print "%s - Liste des RS sans type d'acte : %s" % (service.name, str(rs_without_act_type))
        print "%s - Liste des types d'actes inconnus : %s" % (service.name, str(unknown_act_type_id))
        print "%s - Liste des RS invalides : %s" % (service.name, len(invalid_rs))

        enfant_not_found = set()
        rr_not_found = set()
        rs_without_act_type = set()
        unknown_act_type_id = set()
        invalid_rs = set()
        for rr in rr_data:
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
            # connect enfant
            enfant_id = rr['enfant_id']
            if enfant_id == '0':
                add_invalid(rr, 'not an appointment')
            elif enfant_id in enfant_idx:
                rr['enfant'] = enfant_idx[enfant_id]
            else:
                add_invalid(rr, 'enfant_id not found %s' % enfant_id)
                enfant_not_found.add(enfant_id)
            # connect act_type
            act_type_id = rr['type_acte']
            if act_type_id == '0' and rr['enfant_id'] == '0':
                add_invalid(rr, 'not an appointment')
            elif act_type_id:
                if act_type_id in act_types_idx:
                    rr['act_type'] = act_types_idx[act_type_id]
                else:
                    add_invalid(rr, 'act_type not found %s' % act_type_id)
                    unknown_act_type_id.add(act_type_id)
            else:
                raise NotImplemented
            if rr.get('invalid'):
                invalid_rr_writer.writerow([ unicode(rr[col]).encode('utf-8') for col in rr_cols ])

        # stats
        exceptions = 0
        events = 0
        single = 0
        recurrent = 0
        invalid_single = 0
        invalid_recurrent = 0
        for row in rs_data:
            if row['event']:
                events += 1
            elif row.get('invalid'):
                invalid_single += 1
            elif row['exception']:
                exceptions += 1
            else:
                single += 1
        for row in rr_data:
            if row.get('invalid'):
                invalid_recurrent += 1
            else:
                recurrent += 1
        print ' == Stat == '
        print ' Évènements hors RDV', events
        print ' Rdv individuels', single
        print ' Rdv recurrents', recurrent
        print ' Exceptions', exceptions
        print ' Rdv recurrents invalides', invalid_recurrent
        print ' Rdv individuels invalides', invalid_single

        # create single rdv
        limit = 1000000
        with transaction.commit_manually():
            try:
                # single RS
                i = 0 
                rows = []
                events = []
                for row in rs_data[:limit]:
                    if row['exception'] or row.get('invalid'):
                        continue
                    i += 1
                    rows.append(row)
                    event = EventWithAct.objects.create(patient=row['enfant'],
                            start_datetime=row['start_datetime'],
                            end_datetime=row['end_datetime'],
                            act_type=row['act_type'],
                            old_rs_id=row['id'],
                            room=Room(id=1),
                            title=row['libelle'],
                            description=row['texte'])
                    row['event'] = event
                    events.append(event)
                    print "Rdv creation %-6d\r" % i,
                print
                def batch_bulk(model, rows, limit):
                    i = 0
                    while rows[i:i+limit]:
                        model.objects.bulk_create(rows[i:i+limit])
                        i += limit
                def service_and_workers(events, rows):
                    services = []
                    ServiceThrough = EventWithAct.services.through
                    for event in events:
                        services.append(ServiceThrough(
                            event_id=event.event_ptr_id,
                            service_id=service.id))
                    batch_bulk(ServiceThrough, services, 100)
                    ParticipantThrough = EventWithAct.participants.through
                    participants = []
                    for row, event in zip(rows, events):
                        for worker in row['workers']:
                            participants.append(
                                    ParticipantThrough(
                                        event_id=event.event_ptr_id,
                                        people_id=worker.people_ptr_id))
                    batch_bulk(ParticipantThrough, participants, 100)
                    print 'Created %s service links' % len(services)
                    print 'Created %s participants links' % len(participants)
                service_and_workers(events, rows)
                # RR
                rows = []
                events = []
                i = 0
                for row in rr_data[:limit]:
                    if row.get('invalid'):
                        continue
                    i += 1
                    rows.append(row)
                    event = EventWithAct.objects.create(
                            patient=row['enfant'],
                            start_datetime=row['start_datetime'],
                            end_datetime=row['end_datetime'],
                            act_type=row['act_type'],
                            old_rs_id=row['id'],
                            room=Room(id=1),
                            title=row['libelle'],
                            description=row['texte'],
                            recurrence_periodicity=row['recurrence_periodicity'],
                            recurrence_end_date=row['end_date'])
                    row['event'] = event
                    events.append(event)
                    print "Rdv recurrent creation %-6d\r" % i,
                print
                service_and_workers(events, rows)
                # Exceptions
                excrows = []
                excevents = []
                i = 0
                for rr, event in zip(rows, events):
                    for row in rr['exceptions']:
                        if row.get('invalid'):
                            print 'exception invalide'
                            continue
                        i += 1
                        excrows.append(row)
                        event = EventWithAct.objects.create(
                                patient=row['enfant'],
                                start_datetime=row['start_datetime'],
                                end_datetime=row['end_datetime'],
                                act_type=row['act_type'],
                                old_rs_id=row['id'],
                                room=Room(id=1),
                                title=row['libelle'],
                                description=row['texte'],
                                exception_to=event,
                                exception_date=row['date'])
                        row['event'] = event
                        excevents.append(event)
                        print "Exception creation %-6d\r" % i,
                print
                service_and_workers(excevents, excrows)
            except:
                transaction.rollback()
            else:
                transaction.commit()


        # Clean act for this service
        Act.objects.filter(patient__service=service).delete()
        actes_data, actes_idx, actes_cols = load_csv(db, 'actes')
        act_to_event = dict()
        for row in rs_data:
            if row.get('event') and row['base_id']:
                act_to_event[row['base_id']] = row['event']
        actes = []
        i = 0
        j = 0
        for row in actes_data:
            i += 1
            row['date'] = _to_date(row['date_acte'])
            row['time'] = _to_time(row['horaire'])
            row['duration'] = _to_duration(row['duree'])
            row['is_billed'] = row['marque'] == '1'
            row['validation_locked'] = row['date'] < date(2013, 1, 3)
            set_enfant(row)
            set_act_type(row)
            row['parent_event'] = act_to_event.get(row['id'])
            if row['parent_event']:
                j += 1
            row['state'] = map_cs[service.name].get(row['cs'],
                    'VALIDE')
        print 'Actes:'
        print ' - importe ', i
        print ' - link to rdv', j


    invalid_rs_csv.close()
    invalid_rr_csv.close()

if __name__ == "__main__":
    main()
