# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys
import csv

from datetime import datetime, time, date
from dateutil.relativedelta import relativedelta

import alcide.settings
import django.core.management

django.core.management.setup_environ(alcide.settings)

import logging
logger = logging.getLogger('import_pcs')
log_handler = logging.FileHandler("./scripts/import_pcs.log")
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)s.%(message)s'))
logger.addHandler(log_handler)

from django.contrib.auth.models import User
from django.db import transaction

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from alcide.agenda.models import Event, EventType
from alcide.dossiers.models import PatientRecord, Status, FileState, PatientAddress, PatientContact, \
             SessadHealthCareNotification, HealthCare

from alcide.ressources.models import Service
from alcide.personnes.models import Worker, Holiday, ExternalWorker, ExternalTherapist
from alcide.ressources.models import (WorkerType, ParentalAuthorityType, ParentalCustodyType,
    FamilySituationType, TransportType, TransportCompany, Provenance, AnalyseMotive, FamilyMotive,
    CodeCFTMEA, SocialisationDuration, School, SchoolLevel, OutMotive, OutTo, AdviceGiver,
    MaritalStatusType, Job, PatientRelatedLink, HealthCenter)
from alcide.actes.models import Act

# Configuration
db_path = "./scripts/20130104-213225"

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


#@transaction.commit_manually
def import_dossiers_phase_1():
    status_accueil = Status.objects.filter(type="ACCUEIL")[0]
    status_fin_accueil = Status.objects.filter(type="FIN_ACCUEIL")[0]
    status_diagnostic = Status.objects.filter(type="DIAGNOSTIC")[0]
    status_traitement = Status.objects.filter(type="TRAITEMENT")[0]
    status_clos = Status.objects.filter(type="CLOS")[0]
    status_bilan = Status.objects.filter(type="BILAN")[0]
    status_suivi = Status.objects.filter(type="SUIVI")[0]
    status_surveillance = Status.objects.filter(type="SURVEILLANCE")[0]
    creator = User.objects.get(id=1)

    db = "F_ST_ETIENNE_SESSAD"
    service = Service.objects.get(name="SESSAD DYS")

    pcs_d = {}

    msg = "Lecture de la table des dossiers..."
    logger.info("%s" % msg)
    csvfile = open(os.path.join(db_path, db, 'dossiers.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    d_cols = csvlines.next()
    tables_data['dossiers'] = {}
    for line in csvlines:
        #Au moins nom et prénom
        data = _get_dict(d_cols, line)
        tables_data['dossiers'][line[0]] = data
    csvfile.close()
    msg = "Terminé"
    logger.info("%s" % msg)

    msg = "Chargement des prise en charge..."
    logger.info("%s" % msg)
    csvfile = open(os.path.join(db_path, db, 'pc.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    pc_cols = csvlines.next()
    tables_data['pcs'] = {}
    i = 0
    for line in csvlines:
        data = _get_dict(pc_cols, line)
        pcs_d[line[0]] = data
        if line[1] in tables_data['pcs'].keys():
            tables_data['pcs'][line[1]].append(data)
        else:
            tables_data['pcs'][line[1]] = [data]
        i += 1
    csvfile.close()
    msg = "Terminé : dictionnaire avec clé patient prêt"
    logger.info("%s" % msg)

    msg = "Chargement des periodes prise en charge..."
    logger.info("%s" % msg)
    csvfile = open(os.path.join(db_path, db, 'periodes_pc.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    pc_cols = csvlines.next()
    tables_data['periodes_pcs'] = {}
    j = 0
    for line in csvlines:
        data = _get_dict(pc_cols, line)
        if line[1] in tables_data['periodes_pcs'].keys():
            tables_data['periodes_pcs'][line[1]].append(data)
        else:
            tables_data['periodes_pcs'][line[1]] = [data]
        j += 1
    csvfile.close()
    msg = "Terminé : dictionnaire avec clé prise en charge prêt"
    logger.info("%s" % msg)

    msg = "Nombre de patients concernés par une prise en charge: %d" % len(tables_data['pcs'].keys())
    logger.info("%s" % msg)
    msg = "Nombre de prises en charges à traiter : %d" % i
    logger.info("%s" % msg)
    k = 0
    l = 0
    for dossier_id, pcs in tables_data['pcs'].items():
        if len(pcs) > 1:
            k += 1
        else:
            if pcs[0]['genre_pc'] != '1':
                l += 1
    msg = "Nombre de patients qui ont plus d'une prise en charge : %d" % k
    logger.info("%s" % msg)
    msg = "Nombre de patients qui n'ont qu'une prise en charge mais qui n'est pas de diagnostic diag : %d" % l
    logger.info("%s" % msg)
    msg = "Nombre de periodes pour toutes les prises en charge : %d" % j
    logger.info("%s" % msg)
    k = 0
    l = 0
    m = 0
    for pc, periodes in tables_data['periodes_pcs'].items():
        if len(periodes) > 1:
            k += 1
            if pcs_d[pc]['genre_pc'] != '1':
                l += 1
    msg = "Nombre de prises en charge qui on plus d'une periode : %d" % k
    logger.info("%s" % msg)
    msg = "Nombre de prises en charge diagnostic qui on plus d'une periode : %d" % (k - l)
    logger.info("%s" % msg)
    msg = "Nombre de prises en charge traitement qui on plus d'une periode : %d" % l
    logger.info("%s" % msg)

    histo = {}
    for dossier_id, pcs in tables_data['pcs'].items():
        histo[dossier_id] = []
        for pc in pcs:
            t = pc['genre_pc']
            for periode in tables_data['periodes_pcs'][pc['id']]:
                histo[dossier_id].append(periode)

    author = User.objects.get(pk=1)

#    msg = "Suppression de toutes les notifications existantes dans alcide..."
#    logger.info("%s" % msg)
#    SessadHealthCareNotification.objects.all().delete()
#    msg = "Terminé"
#    logger.info("%s" % msg)
    # Creation des Healthcare
    msg = "Création des notifications..."
    logger.info("%s" % msg)
    i = 0
    for patient_id, pcs in histo.items():
        patient = None
        try:
            patient = PatientRecord.objects.get(old_id=patient_id, service=service)
        except:
            msg = "Patient présent dans la table des prises en charge mais pas dans alcide"
            logger.error("%s" % msg)
            msg = "Anciens ID : %s - Nom : %s - Prénom : %s" % (patient_id, str(tables_data['dossiers'][patient_id]['nom'].encode('utf-8')), str(tables_data['dossiers'][patient_id]['prenom'].encode('utf-8')))
            logger.error("%s" % msg)
            continue
        HealthCare.objects.filter(patient=patient).delete()
        SessadHealthCareNotification.objects.filter(patient=patient).delete()
        for pc in pcs:
            start_date = _to_date(pc['date_debut'])
            end_date = _to_date(pc['date_fin'])
            request_date = _to_date(pc['date_demande'])
            agree_date = _to_date(pc['date_accord'])
            insist_date = _to_date(pc['date_relance'])
            hc = SessadHealthCareNotification(start_date=start_date,
                end_date=end_date,
                request_date=request_date,
                agree_date=agree_date,
                insist_date=insist_date,
                patient=patient,
                author=author)
            hc.save()
            i += 1
    msg = "Création des %d notifications terminée" % i
    logger.info("%s" % msg)

if __name__ == "__main__":
    msg = "Lancement du script"
    logger.info("%s" % msg)

    import_dossiers_phase_1()

    msg = "Fin du script"
    logger.info("%s" % msg)
