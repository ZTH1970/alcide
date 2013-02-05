# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys
import csv

from datetime import datetime, time, date
from dateutil.relativedelta import relativedelta

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

import logging
logger = logging.getLogger('import_pcs')
log_handler = logging.FileHandler("./scripts/import_pcs.log")
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)s.%(message)s'))
logger.addHandler(log_handler)

from django.contrib.auth.models import User
from django.db import transaction

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from calebasse.agenda.models import Event, EventType
from calebasse.dossiers.models import PatientRecord, Status, FileState, PatientAddress, PatientContact, \
             CmppHealthCareDiagnostic, CmppHealthCareTreatment

from calebasse.ressources.models import Service
from calebasse.personnes.models import Worker, Holiday, ExternalWorker, ExternalTherapist
from calebasse.ressources.models import (WorkerType, ParentalAuthorityType, ParentalCustodyType,
    FamilySituationType, TransportType, TransportCompany, Provenance, AnalyseMotive, FamilyMotive,
    CodeCFTMEA, SocialisationDuration, School, SchoolLevel, OutMotive, OutTo, AdviceGiver,
    MaritalStatusType, Job, PatientRelatedLink, HealthCenter)
from calebasse.actes.models import Act

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

    db = "F_ST_ETIENNE_CMPP"
    service = Service.objects.get(name="CMPP")

    pcs_d = {}

    acts_ids = [
                '193815',
                '173334',
                '171872',
                '193506',
                '182039',
                '166806',
                '183054',
                '181050',
                '172301',
                '193914',
                '186876',
                '161111',
               ]

    msg = "Chargement des actes..."
    logger.info("%s" % msg)
    csvfile = open(os.path.join(db_path, db, 'actes.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    pc_cols = csvlines.next()
    tables_data['actes'] = {}
    tables_data['actes']['nf'] = []
    for line in csvlines:
        data = _get_dict(pc_cols, line)
        if _exist(line[6]):
            if line[6] in tables_data['actes'].keys():
                tables_data['actes'][line[6]].append(data)
            else:
                tables_data['actes'][line[6]] = [data]
        else:
            tables_data['actes']['nf'].append(data)
    csvfile.close()
    msg = "Terminé : dictionnaire avec clé facture prêt"
    logger.info("%s" % msg)

    msg = "Chargement des factures..."
    logger.info("%s" % msg)
    csvfile = open(os.path.join(db_path, db, 'factures.csv'), 'rb')
    csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
    pc_cols = csvlines.next()
    tables_data['factures'] = {}
    for line in csvlines:
        data = _get_dict(pc_cols, line)
        if line[7] in tables_data['factures'].keys():
            tables_data['factures'][line[7]].append(data)
        else:
            tables_data['factures'][line[7]] = [data]
    csvfile.close()
    msg = "Terminé : dictionnaire avec clé période de pc prêt"
    logger.info("%s" % msg)

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

    j = 0
    k = 0
    nb_actes_diag = [0 for i in range(20)]
    nb_actes_trait = [0 for i in range(100)]
    periode_ss_fact = []
    facture_ss_actes = []
    histo = {}
    facturations = {}
    total_factures = []
    for dossier_id, pcs in tables_data['pcs'].items():
        histo[dossier_id] = []
        for pc in pcs:
            t = pc['genre_pc']
            for periode in tables_data['periodes_pcs'][pc['id']]:
                if not _exist(periode['date_debut']):# or _to_date(periode['date_debut']) < datetime(year=2002, month=1, day=1):
                    continue
                my_pc = {}
                my_pc['type'] = t
                my_pc['periode'] = periode
                # Il n'y qu'au cmpp où il y a des factures
                # pour le sessad dy, on ajoute juste les periodes pour indiquer les notifications
                # Dans les autres services, rien ?
                factures = tables_data['factures'].get(periode['ppc_id'], None)
                my_pc['factures'] = []
                my_pc['actes'] = []
                if factures:
                    total_factures += [f['id'] for f in factures]
                    for facture in factures:
                        if facture['pc_id'] != pc['id']:
                            print "%s != %s" % (facture['pc_id'], pc['id'])
                        num = facture['numero']
                        actes = tables_data['actes'].get(num, None)
                        if actes:
                            my_pc['factures'].append((facture, actes))
                            my_pc['actes'] += actes
                            fact_num = facture['numero'][0:3]
                            if not fact_num in facturations:
                                facturations[fact_num] = {}
                                facturations[fact_num]['factures'] = []
                                facturations[fact_num]['actes'] = []
                            facturations[fact_num]['factures'].append(facture)
                            facturations[fact_num]['actes'] += actes
                        else:
                            facture_ss_actes.append(facture['id'])
                else:
                    periode_ss_fact.append(periode)
                    if t == '1':
                        k += 1
                if t == '1':
                    nb_actes_diag[len(my_pc['actes'])] += 1
                else:
                    nb_actes_trait[len(my_pc['actes'])] += 1
                histo[dossier_id].append(my_pc)
                j += len(my_pc['actes'])
    msg = "Nombre de factures : %d" % len(total_factures)
    logger.info("%s" % msg)
    diff = len(total_factures) - len(set(total_factures))
    if diff > 0:
        msg = "Il y a des factures en doubles : %d" % diff
        logger.warn("%s" % msg)
    msg = "Nombre d'actes : %d" % j
    logger.info("%s" % msg)
    # Ca arrive surtout avant car ajout periode auto sans qu'il y ait de facturation derriere
    msg = "Periodes sans factures, donc sans actes : %d" % len(periode_ss_fact)
    logger.info("%s" % msg)
    msg = "Periodes sans factures de type diagnostic : %d" % k
    logger.info("%s" % msg)
    msg = "Periodes sans factures de type traitraitement : %d" % (len(periode_ss_fact) - k)
    logger.info("%s" % msg)
    # Ca arrive aussi
    msg = "Factures sans actes : %d %s" % (len(facture_ss_actes), str(facture_ss_actes))
    logger.warn("%s" % msg)

    msg = "Nombre d'actes par prises en charge de diagnostique :"
    logger.info("%s" % msg)
    i = 0
    for val in nb_actes_diag:
        msg = "%d : %d" % (i, val)
        logger.info("%s" % msg)
        i += 1
    msg = "Nombre d'actes par prises en charge de traitement :"
    logger.info("%s" % msg)
    i = 0
    for val in nb_actes_trait:
        msg = "%d : %d" % (i, val)
        logger.info("%s" % msg)
        i += 1

    for num, values in facturations.items():
        msg = "Nombre de facturations : %s" % num
        logger.info("%s" % msg)
        msg = "Nombre de factures (hors factures sans actes) : %d" % len(values['factures'])
        logger.info("%s" % msg)
        msg = "Nombre d'actes : %d" % len(values['actes'])
        logger.info("%s" % msg)

    author = User.objects.get(pk=1)

#    msg = "Suppression de toutes les prises en charge existante dans calebasse..."
#    logger.info("%s" % msg)
#    CmppHealthCareDiagnostic.objects.all().delete()
#    CmppHealthCareTreatment.objects.all().delete()
#    msg = "Terminé"
#    logger.info("%s" % msg)
    # Creation des Healthcare
    HcDiags = []
    HcTraits = []
    msg = "Recherche des prises en charge..."
    logger.info("%s" % msg)
    for patient_id, pcs in histo.items():
        patient = None
        try:
            patient = PatientRecord.objects.get(old_id=patient_id, service=service)
        except:
            msg = "Patient présent dans la table des prises en charge mais pas dans calebasse"
            logger.error("%s" % msg)
            msg = "Anciens ID : %s - Nom : %s - Prénom : %s" % (patient_id, str(tables_data['dossiers'][patient_id]['nom']), str(tables_data['dossiers'][patient_id]['prenom']))
            logger.error("%s" % msg)
            continue
        for pc in pcs:
            start_date = _to_date(pc['periode']['date_debut'])
            request_date = _to_date(pc['periode']['date_demande'])
            agree_date = _to_date(pc['periode']['date_accord'])
            insist_date = _to_date(pc['periode']['date_relance'])
            act_number = _to_int(pc['periode']['nbr_seances']) or 0
            if pc['type'] == '1':
#                    if act_number != 6:
#                        print "PC diag pour %d avec nombre d'acte pris en charge de %d" % (patient.id, act_number)
                hc = CmppHealthCareDiagnostic.objects.get(start_date=start_date,
                    request_date=request_date,
                    agree_date=agree_date,
                    insist_date=insist_date,
                    patient=patient,
                    act_number=act_number,
                    author=author)
            else:
#                    if act_number != 30:
#                        print "PC diag pour %d avec nombre d'acte pris en charge de %d" % (patient.id, act_number)
                hc = CmppHealthCareTreatment.objects.get(start_date=start_date,
                    request_date=request_date,
                    agree_date=agree_date,
                    insist_date=insist_date,
                    patient=patient,
                    act_number=act_number,
                    author=author)
            pc['hc'] = hc
    msg = "Recherche des prises en charge terminée"
    logger.info("%s" % msg)
    #CmppHealthCareDiagnostic.objects.bulk_create(HcDiags)
    #CmppHealthCareTreatment.objects.bulk_create(HcTraits)
    # Association des actes au healthcare

    msg = "Association des actes dans calebasse aux prises en charge..."
    logger.info("%s" % msg)
    i = 0
    j = 0
    for patient_id, pcs in histo.items():
        patient = None
        try:
            patient = PatientRecord.objects.get(old_id=patient_id, service=service)
        except:
#                print 'Patient %s non trouve (2)' % patient_id
            continue
        for pc in pcs:
            hc = pc['hc']
            for act in pc['actes']:
                if act['id'] in acts_ids:
                    msg = "Traitement de %s" % str(act['id'])
                    logger.info("%s" % msg)
                    a = None
                    try:
                        a = Act.objects.get(old_id=act['id'], patient__service=service)
                    except ObjectDoesNotExist:
                        msg = "Acte pointé par une facture avec ancien ID %s non trouvé" % str(act['id'])
                        logger.error("%s" % msg)
                        i += 1
                        continue
                    except MultipleObjectsReturned:
                        msg = "Acte pointé par une facture avec ancien ID %s existe plusieurs fois" % str(act['id'])
                        logger.error("%s" % msg)
                        i += 1
                        continue
                    except Exception, e:
                        msg = "Acte pointé par une facture avec ancien ID %s lève %s" % (str(act['id']), str(e))
                        logger.error("%s" % msg)
                        i += 1
                        continue
                    if not a.is_billed:
                        msg = "Acte trouvé et pris en charge mais non marqué facturé dans calebasse, marquage facturé (ID acte calebasse : %d)" % a.id
                        logger.warn("%s" % msg)
                        a.is_billed = True
                    a.healthcare = hc
                    a.save()
                    j += 1
    msg = "Actes non trouvés : %d" % i
    logger.info("%s" % msg)
    msg = "Actes facturés chez Faure et réimputés dans calebasse aux prises en charge : %d" % j
    logger.info("%s" % msg)

if __name__ == "__main__":
    msg = "Lancement du script"
    logger.info("%s" % msg)

    import_dossiers_phase_1()

    msg = "Fin du script"
    logger.info("%s" % msg)
