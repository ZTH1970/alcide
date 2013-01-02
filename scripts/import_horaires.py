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

from calebasse.actes.models import EventAct
from calebasse.agenda.models import Event, EventType
from calebasse.dossiers.models import PatientRecord, Status, FileState
from calebasse.ressources.models import Service
from calebasse.personnes.models import Worker, Holiday, TimeTable, PERIODICITIES
from calebasse.personnes.forms import PERIOD_LIST_TO_FIELDS
from calebasse.ressources.models import WorkerType, HolidayType

# Configuration
db_path = "./scripts/20121221-192258"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]


def _to_date(str_date):
    if not str_date:
        return None
    return datetime.strptime(str_date[:-13], "%Y-%m-%d")

def _to_int(str_int):
    if not str_int:
        return None
    return int(str_int)

def discipline_mapper(tables_data, service):
    for line in tables_data['discipline']:
        # Insert workertype
        if not WorkerType.objects.filter(name=line['libelle']):
            WorkerType.objects.create(name=line['libelle'])


def intervenants_mapper(tables_data, service):
    for line in tables_data['intervenants']:
        # Insert workers
        for disp in tables_data['discipline']:
            if disp['id'] == line['discipline']:
                type = WorkerType.objects.get(name=disp['libelle'])
        # TODO : import actif or not
        worker, created = Worker.objects.get_or_create(
                type=type,
                last_name=line['nom'],
                first_name=line['prenom'],
                email=line['email'],
                phone=line['tel'],
                gender=int(line['titre']),
                )
        worker.services.add(service)

def dossiers_mapper(tables_data, service):
    global dossiers
    for line in tables_data['dossiers']:
        status = Status.objects.filter(type="ACCUEIL").filter(services=service)
        creator = User.objects.get(id=1)
        gender = _to_int(line['nais_sexe'])
        if gender == 0:
            gender = None
        # TODO: add more fields
        patient, created = PatientRecord.objects.get_or_create(first_name=line['prenom'],
                last_name=line['nom'], birthdate=_to_date(line['nais_date']),
                twinning_rank=_to_int(line['nais_rang']),
                gender=gender, service=service, creator=creator)
        dossiers[line['id']] = patient

        if not created:
            if not line['ins_date']:
                # Hack when there is no inscription date put 01/01/1970
                line['ins_date'] = "1970-01-01 00:00:00.000"
            fs = FileState.objects.create(status=status[0], author=creator,
                   date_selected=_to_date(line['ins_date']),
                    previous_state=None, patient=patient)
            patient.last_state = fs
            patient.save()
            if line['sor_date']:
                status = Status.objects.filter(type="CLOS").filter(services=service)
                fs = FileState.objects.create(status=status[0], author=creator,
                        date_selected=_to_date(line['sor_date']),
                        previous_state=None, patient=patient)
                patient.last_state = fs
                patient.save()

def rs_mapper(tables_data, service):
    global dossiers

    event_type = EventType.objects.get(
                label=u"Rendez-vous patient"
                )

    for line in tables_data['rs']:
        if dossiers.has_key(line['enfant_id']):
            patient = dossiers[line['enfant_id']]
            strdate = line['date_rdv'][:-13] + ' ' + line['heure'][11:-4]
            date = datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S")

             # TODO: add act_type
#            act_event = EventAct.objects.get_or_create(
#                    title=line['libelle'],
#                    event_type=event_type,
#                    patient=patient,
#                    act_type=act_type,
#                    date=date
#                    )
        else:
            # TODO: if no patient add event
            pass


def conge_mapper(tables_data, service):
    """ """
    for line in tables_data['conge']:
        pass

def ev_mapper(tables_data, service):
    """ """
    pass

def notes_mapper(tables_data, service):
    """ """
    pass

def _get_dict(cols, line):
    """"""
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res

tables_data = {}

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


def main():
    """ """

    thera_evt = {}
    cf = open('./scripts/horaires_manuel.csv', 'wb')
    writer = csv.writer(cf, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Jour', 'Nom', 'Prénom', 'Libellé',
        'Date début', 'Date fin', 'Horaire', 'Périodicité'])


    for db in dbs:
        if "F_ST_ETIENNE_CMPP" == db:
            service = Service.objects.get(name="CMPP")
        elif "F_ST_ETIENNE_CAMSP" == db:
            service = Service.objects.get(name="CAMSP")
        elif "F_ST_ETIENNE_SESSAD_TED" == db:
            service = Service.objects.get(name="SESSAD TED")
        elif "F_ST_ETIENNE_SESSAD" == db:
            service = Service.objects.get(name="SESSAD DYS")

        tables_data[service.name] = []
        csvfile = open(os.path.join(db_path, db, 'ev.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        i = 0
        for line in csvlines:
            if line[8].upper() == 'ARRIVEE' or line[8].upper() == 'DEPART':
                data = _get_dict(cols, line)
                tables_data[service.name].append(data)
                i += 1
        csvfile.close()

        print "%s - Nombre d'evt horaires : %d" % (service.name, i)

        thera_evt[service.name] = {}
        csvfile = open(os.path.join(db_path, db, 'details_ev.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        not_found = []
        for line in csvlines:
            worker = None
            try:
                if service.name == 'CMPP':
                    worker = Worker.objects.get(old_cmpp_id=line[2])
                elif service.name == 'CAMSP':
                    worker = Worker.objects.get(old_camsp_id=line[2])
                elif service.name == 'SESSAD DYS':
                    worker = Worker.objects.get(old_sessad_dys_id=line[2])
                elif service.name == 'SESSAD TED':
                    worker = Worker.objects.get(old_sessad_ted_id=line[2])
                else:
                    print "service inconnu!!!"
                    exit(0)
            except Exception, e:
                not_found.append(line[2])
            if worker:
                workers = thera_evt.setdefault(line[1], [])
                workers.append(worker)
        csvfile.close()

        print "%s - Liste des worker not found : %s" % (service.name, str(set(not_found)))
        # 7 8 17 n'existe pas au SESSAD TED
        # ['91', '89', '17', '77', '76', '75', '74', '73', '72', '82', '90', '85'] n'existe pas au CMPP

        i = 0
        j = 0
        dic_worker[service.name] = {}
        for horaire in tables_data[service.name]:
            if not horaire['id'] in thera_evt[service.name]:
                j += 1
            elif not thera_evt[service.name][horaire['id']]:
                i += 1
            else:
                if len(thera_evt[service.name][horaire['id']]) > 1:
                    print "%s - Horaire %s avec plus d'un worker %s!" % (service.name, horaire['id'], str(len(thera_evt[service.name][horaire['id']])))
                    exit(0)
                worker = thera_evt[service.name][horaire['id']][0]
                if not worker in dic_worker[service.name].keys():
                    dic_worker[service.name][worker] = {}
                if 'horaires' in dic_worker[service.name][worker].keys():
                    dic_worker[service.name][worker]['horaires'].append(horaire)
                else:
                    dic_worker[service.name][worker]['horaires'] = [horaire]

        for worker, details in dic_worker[service.name].items():
            for horaire in details['horaires']:
                date_fin = None
                if 'date_fin' in horaire and horaire['date_fin'] != '':
                    date_fin = datetime.strptime(horaire['date_fin'][:-13], "%Y-%m-%d")
                if not date_fin or date_fin > datetime.today():
                    start_date = datetime.strptime(horaire['date_debut'][:-13], "%Y-%m-%d").date()
                    weekday = int(start_date.strftime('%w'))
                    if weekday in dic_worker[service.name][worker].keys():
                        dic_worker[service.name][worker][weekday].append(horaire)
                    else:
                        dic_worker[service.name][worker][weekday] = [horaire]
            for i in range(0,8):
                if i in dic_worker[service.name][worker].keys():
                    horaires = sorted(dic_worker[service.name][worker][weekday], key=lambda tup: tup['date_debut'])
                    dic_worker[service.name][worker][weekday] = horaires

        i = 0
        j = 0
        for worker in  dic_worker[service.name].keys():
            for day, horaires in  dic_worker[service.name][worker].items():
                if day != 'horaires':
                    i += 1
                    if len(horaires) > 2 or len(horaires)%2:
                        print 'A'
                        for horaire in horaires:
                            print [day, worker.last_name, horaire['libelle'], horaire['date_debut']]
                            for k, v in PERIODICITIES:
                                if PERIOD_FAURE_NOUS[int(horaire['rythme'])] == k:
                                    p = v
                                    break
                            d = JOURS[day]
                            writer.writerow([d, worker.last_name.encode('utf-8'), worker.first_name.encode('utf-8'), horaire['libelle'],
                                horaire['date_debut'], horaire['date_fin'], horaire['heure'], p])
                    else:
                        arrivee = None
                        depart = None
                        for horaire in horaires:
                            if horaire['libelle'] == 'ARRIVEE':
                                arrivee = horaire
                            else:
                                depart = horaire
                        if not (arrivee and depart):
                            print 'B'
                            for horaire in horaires:
                                print [day, worker.last_name, horaire['libelle'], horaire['date_debut']]
                                for k, v in PERIODICITIES:
                                    if PERIOD_FAURE_NOUS[int(horaire['rythme'])] == k:
                                        p = v
                                        break
                                d = JOURS[day]
                                writer.writerow([d, worker.last_name.encode('utf-8'), worker.first_name.encode('utf-8'), horaire['libelle'],
                                    horaire['date_debut'], horaire['date_fin'], horaire['heure'], p])
                        else:
                            j += 1
                            # Créer les horaires
                            start_date = datetime.strptime(arrivee['date_debut'][:-13], "%Y-%m-%d").date()
                            weekday = day - 1
                            periodicity = PERIOD_FAURE_NOUS[int(arrivee['rythme'])]
                            if not periodicity:
                                periodicity = 1
                            week_period, week_parity, week_rank = PERIOD_LIST_TO_FIELDS[periodicity - 1]
                            end_date = None
                            skip = False
                            if arrivee['date_fin']:
                                end_date = datetime.strptime(arrivee['date_fin'][:-13], "%Y-%m-%d").date()
                            tt = TimeTable(worker=worker,
                            weekday=weekday,
                            periodicity=periodicity,
                            week_period=week_period, week_parity=week_parity, week_rank=week_rank,
                            start_time = datetime.strptime(arrivee['heure'][11:16], "%H:%M").time(),
                            end_time = datetime.strptime(depart['heure'][11:16], "%H:%M").time(),
                            start_date = start_date,
                            end_date = end_date)
                            tt.save()
                            tt.services.add(service)
                            print '====> %s %s' % (worker.last_name.encode('utf-8'), worker.first_name.encode('utf-8'))


        print i
        print j

    csvfile.close()

if __name__ == "__main__":
    main()
