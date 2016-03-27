# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys
import csv

from datetime import datetime, time
from dateutil.relativedelta import relativedelta

import alcide.settings
import django.core.management

django.core.management.setup_environ(alcide.settings)

from django.contrib.auth.models import User

from alcide.agenda.models import Event, EventType
from alcide.dossiers.models import PatientRecord, Status, FileState, PatientAddress, PatientContact
from alcide.ressources.models import Service
from alcide.personnes.models import Worker, Holiday, ExternalWorker, ExternalTherapist
from alcide.ressources.models import (WorkerType, ParentalAuthorityType, ParentalCustodyType,
    FamilySituationType, TransportType, TransportCompany, Provenance, AnalyseMotive, FamilyMotive,
    CodeCFTMEA, SocialisationDuration, School, SchoolLevel, OutMotive, OutTo, AdviceGiver,
    MaritalStatusType, Job, PatientRelatedLink, HealthCenter)

# Configuration
db_path = "./scripts/20130104-213225"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
#dbs = ["F_ST_ETIENNE_SESSAD_TED"]

import logging
logger = logging.getLogger('import_pcs')
log_handler = logging.FileHandler("./scripts/import_centres_contacts_manquants.log")
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)s.%(message)s'))
logger.addHandler(log_handler)

map_cs = {}
map_cs['CAMSP'] = {
'1': 'ACT_DOUBLE',
'2': 'ABS_NON_EXC',
'3': 'ABS_EXC',
'4': 'ABS_INTER',
'5': 'ACT_LOST',
'6': 'ANNUL_NOUS',
'7': 'ANNUL_FAMILLE',
'8': 'ENF_HOSP',
'9': 'ACT_LOST',
'10': 'ACT_LOST',
'11': 'ACT_LOST',
'12': 'REPORTE'
}

map_cs['CMPP'] = {
'1': 'ACT_DOUBLE',
'2': 'ABS_NON_EXC',
'3': 'ABS_EXC',
'4': 'ABS_INTER',
'5': 'ACT_LOST',
'6': 'ANNUL_NOUS',
'7': 'ANNUL_FAMILLE',
'8': 'ABS_ESS_PPS',
'9': 'ACT_LOST',
'10': 'ACT_LOST',
'11': 'ACT_LOST',
'12': 'REPORTE'
}

map_cs['SESSAD DYS'] = {
'1': 'ACT_DOUBLE',
'2': 'ABS_NON_EXC',
'3': 'ABS_EXC',
'4': 'ABS_INTER',
'5': 'ACT_LOST',
'6': 'ANNUL_NOUS',
'7': 'ANNUL_FAMILLE',
'8': 'ABS_ESS_PPS',
'9': 'ACT_LOST',
'10': 'ACT_LOST',
'11': 'REPORTE'
}


map_cs['SESSAD TED'] = {
'1': 'ACT_DOUBLE',
'2': 'ABS_NON_EXC',
'3': 'ABS_EXC',
'4': 'ACT_LOST',
'5': 'ABS_INTER',
'6': 'ANNUL_NOUS',
'7': 'ANNUL_FAMILLE',
'8': 'REPORTE'
}

def _exist(str):
    if str and str != "" and str != '0':
        return True
    return False

def treat_name(name):
    res = ''
    for p in name.split():
        res += p[0].upper()+p[1:].lower()
        res += ' '
    return res[:-1]

def _to_date(str_date):
    if not str_date:
        return None
    return datetime.strptime(str_date[:-13], "%Y-%m-%d")

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

tables_data = {}

map_rm_cmpp = [1, 3, 2, 8, 6, 4]

def get_rm(service, val):
    old_id_rm = _to_int(val)
    if old_id_rm < 1 or 'SESSAD' in service.name:
        return None
    if service.name == 'CMPP':
        old_id_rm = map_rm_cmpp[old_id_rm - 1]
    try:
        return MaritalStatusType.objects.get(id=old_id_rm)
    except:
        return None

map_job_camsp = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 25, 21, 23, 20, 17, 15, 18, 16, 26, 27, 28]

# CMPP à 25 = Rien
def get_job(service, val):
    old_id_job = _to_int(val)
    if old_id_job < 1:
        return None
    if service.name == 'CAMSP' and old_id_job == 26:
        return None
    if service.name == 'CAMSP':
        try:
            old_id_job = map_job_camsp[old_id_job - 1]
        except:
            print 'Old id job out of range: %d' % old_id_job
    try:
        return Job.objects.get(id=old_id_job)
    except:
        return None

def extract_phone(val):
    if not val or val == '' or val == '0':
        return None
    s = ''.join([c for c in val if c.isdigit()])
    return s[:11]

def get_nir(nir, key, writer, line, service):
    if not nir:
        return None
    if len(nir) != 13:
        return -1
    if key:
        minus = 0
        # Corsica dept 2A et 2B
        if nir[6] in ('A', 'a'):
            nir = [c for c in nir]
            nir[6] = '0'
            nir = ''.join(nir)
            minus = 1000000
        elif nir[6] in ('B', 'b'):
            nir = [c for c in nir]
            nir[6] = '0'
            nir = ''.join(nir)
            minus = 2000000
        try:
            nir = int(nir) - minus
            good_key = 97 - (nir % 97)
            key = int(key)
            if key != good_key:
                msg = 'Clé incorrect %s pour %s' % (str(key), str(nir))
                writer.writerow(line + [service.name, msg])
        except:
            pass
    return nir


def import_dossiers_phase_1():
    """ """
    print "====== Début à %s ======" % str(datetime.today())

    f1 = open('./scripts/dossiers_ecoles_manuel.csv', 'wb')
    writer1 = csv.writer(f1, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    f2 = open('./scripts/dossiers_manuel.csv', 'wb')
    writer2 = csv.writer(f2, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    f3 = open('./scripts/contacts_manuel.csv', 'wb')
    writer3 = csv.writer(f3, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    f4 = open('./scripts/pc_manuel.csv', 'wb')
    writer4 = csv.writer(f4, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    status_accueil = Status.objects.filter(type="ACCUEIL")[0]
    status_diagnostic = Status.objects.filter(type="DIAGNOSTIC")[0]
    status_traitement = Status.objects.filter(type="TRAITEMENT")[0]
    status_clos = Status.objects.filter(type="CLOS")[0]
    status_bilan = Status.objects.filter(type="BILAN")[0]
    status_suivi = Status.objects.filter(type="SUIVI")[0]
    status_surveillance = Status.objects.filter(type="SURVEILLANCE")[0]
    creator = User.objects.get(id=1)

    for db in dbs:
        if "F_ST_ETIENNE_CMPP" == db:
            service = Service.objects.get(name="CMPP")
        elif "F_ST_ETIENNE_CAMSP" == db:
            service = Service.objects.get(name="CAMSP")
        elif "F_ST_ETIENNE_SESSAD_TED" == db:
            service = Service.objects.get(name="SESSAD TED")
        elif "F_ST_ETIENNE_SESSAD" == db:
            service = Service.objects.get(name="SESSAD DYS")

        print "====== %s ======" % service.name
        print datetime.today()


        print "--> Chargement des prise en charge..."
        csvfile = open(os.path.join(db_path, db, 'pc.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        pc_cols = csvlines.next()
        tables_data['pcs'] = []
        for line in csvlines:
            data = _get_dict(pc_cols, line)
            tables_data['pcs'].append(data)
        csvfile.close()
        print "<-- Terminé"

        for pc in tables_data['pcs']:
            if _exist(pc['centre']) and _exist(pc['contact_id']):
                while len(pc['centre']) < 4:
                    pc['centre'] = ['0', pc['centre']]
                    pc['centre'] = ''.join(pc['centre'])
                contact = None
                try:
                    contact = PatientContact.objects.get(old_contact_id=pc['contact_id'])
                except Exception, e:
                    try:
                        patient = PatientRecord.objects.get(old_id=pc['enfant_id'], service=service)
                        if not patient.policyholder:
                            msg = "Patient %s avec centre %s n'a pas de policyholder ?" % (pc['enfant_id'], pc['centre'])
                            logger.error("%s" % msg)
                        else:
                            if not patient.policyholder.other_health_center or patient.policyholder.other_health_center == '0000':
                                patient.policyholder.other_health_center = pc['centre']
                                patient.policyholder.save()
                            elif patient.policyholder.other_health_center != pc['centre']:
                                msg = "Patient %s avec centre %s a un policyholder avec centre %s different" % (pc['enfant_id'], pc['centre'], patient.policyholder.other_health_center)
                                logger.error("%s" % msg)
                    except Exception, e:
                        msg = "Patient %s avec centre %s non trouve" % (pc['enfant_id'], pc['centre'])
                        logger.warn("%s" % msg)
                if contact:
                    contact.other_health_center = pc['centre']
                    contact.save()

    print "====== Fin à %s ======" % str(datetime.today())

if __name__ == "__main__":
    import_dossiers_phase_1()
