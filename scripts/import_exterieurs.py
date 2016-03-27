# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv

from datetime import datetime, time

import alcide.settings
import django.core.management

django.core.management.setup_environ(alcide.settings)

from django.contrib.auth.models import User

from alcide.actes.models import EventAct
from alcide.agenda.models import Event, EventType
from alcide.dossiers.models import PatientRecord, Status, FileState
from alcide.ressources.models import Service
from alcide.personnes.models import Worker, Holiday, ExternalTherapist, ExternalWorker
from alcide.ressources.models import WorkerType

# Configuration
db_path = "./scripts/20121221-192258"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]

# Global mappers. This dicts are used to map a Faure id with a alcide object.
dossiers = {}

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

        unknown_type = WorkerType.objects.get(name="Non défini")

        l = []
        csvfile = open(os.path.join(db_path, db, 'intervenants_exterieurs.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        for line in csvlines:
            data = _get_dict(cols, line)
            l.append(data)
        csvfile.close()

        for intervenant in l:
            dn = intervenant['nom'].upper() + ' ' + intervenant['prenom']
            ExternalWorker(last_name = intervenant['nom'],
                first_name = intervenant['prenom'],
                display_name = dn,
                email = intervenant['email'],
                phone = intervenant['tel_port'],
                phone_work = intervenant['tel_trav'],
                description = intervenant['specialite'],
                address = intervenant['voie'],
                zip_code = intervenant['codepostal'],
                city = intervenant['ville'],
                type = unknown_type,
                old_id = intervenant['id'], old_service=service.name).save()

        l = []
        csvfile = open(os.path.join(db_path, db, 'medecins_exterieurs.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        for line in csvlines:
            data = _get_dict(cols, line)
            l.append(data)
        csvfile.close()

        for intervenant in l:
            dn = intervenant['nom'].upper() + ' ' + intervenant['prenom']
            ExternalTherapist(last_name = intervenant['nom'],
                first_name = intervenant['prenom'],
                display_name = dn,
                email = intervenant['email'],
                phone = intervenant['tel_port'],
                phone_work = intervenant['tel_trav'],
                description = intervenant['specialite'],
                address = intervenant['voie'],
                zip_code = intervenant['codepostal'],
                city = intervenant['ville'],
                type = unknown_type,
                old_id = intervenant['id'], old_service=service.name).save()


if __name__ == "__main__":
    main()
