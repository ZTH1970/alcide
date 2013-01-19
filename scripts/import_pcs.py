# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys
import csv

from datetime import datetime, time
from dateutil.relativedelta import relativedelta

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from django.contrib.auth.models import User

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

#dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
dbs = ["F_ST_ETIENNE_CMPP"]


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

#    f1 = open('./scripts/dossiers_ecoles_manuel.csv', 'wb')
#    writer1 = csv.writer(f1, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

#    f2 = open('./scripts/dossiers_manuel.csv', 'wb')
#    writer2 = csv.writer(f2, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

#    f3 = open('./scripts/contacts_manuel.csv', 'wb')
#    writer3 = csv.writer(f3, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    f4 = open('./scripts/pc_manuel_phase2.csv', 'wb')
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

        pcs_d = {}

        print "--> Chargement des actes..."
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
        print "<-- Terminé : dictionnaire avec clé facture prêt"

        print "--> Chargement des factures..."
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
        print "<-- Terminé : dictionnaire avec clé période de pc prêt"

        print "--> Chargement des prise en charge..."
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
        print "<-- Terminé : dictionnaire avec clé patient prêt"

        print "--> Chargement des periodes prise en charge..."
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
        print "<-- Terminé : dictionnaire avec clé prise en charge prêt"

        print "Nombre de patients : %d" % len(tables_data['pcs'].keys())
        print "Nombre de pc : %d" % i
        k = 0
        l = 0
        for dossier_id, pcs in tables_data['pcs'].items():
            if len(pcs) > 1:
                k += 1
            else:
                if pcs[0]['genre_pc'] != '1':
                    l += 1
        print "Nombre de patient qui ont plus d'une pc : %d" % k
        print "Nombre de patient qui n'ont qu'une pc mais pas diag : %d" % l
        print "Nombre de periodes : %d" % j
        k = 0
        l = 0
        m = 0
        for pc, periodes in tables_data['periodes_pcs'].items():
            if len(periodes) > 1:
                k += 1
                if pcs_d[pc]['genre_pc'] != '1':
                    l += 1
        print "Nombre de pc qui on plus d'une periode : %d" % k
        print "Nombre de pc qui on plus d'une periode qui sont en trait : %d" % l

        i = 0
        j = 0
        k = 0
        nb_actes_diag = [0 for i in range(20)]
        nb_actes_trait = [0 for i in range(100)]
        periode_ss_fact = []
        facture_ss_actes = []
        histo = {}
        facturations = {}
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
                                facture_ss_actes.append(facture)
                    else:
                        periode_ss_fact.append(periode)
                        if t == '1':
                            k += 1
                    if t == '1':
                        nb_actes_diag[len(my_pc['actes'])] += 1
                    else:
                        nb_actes_trait[len(my_pc['actes'])] += 1
                    histo[dossier_id].append(my_pc)
                    i += len(my_pc['factures'])
                    j += len(my_pc['actes'])
        print "Factures : %d" % i
        print "Actes : %d" % j
        # Ca arrive surtout avant car ajout periode auto sans qu'il y ait de facturation derriere
        print "Periodes sans factures, donc sans actes : %d" % len(periode_ss_fact)
        print "Periodes sans factures diag : %d" % k
        print "Periodes sans factures trait : %d" % (len(periode_ss_fact) - k)
        # Ca arrive aussi
        print "Factures sans actes, aïe : %d" % len(facture_ss_actes)

        print "Nombre d'actes par pc diag"
        i = 0
        for val in nb_actes_diag:
            print "%d : %d" % (i, val)
            i += 1
        print "Nombre d'actes par pc trait"
        i = 0
        for val in nb_actes_trait:
            print "%d : %d" % (i, val)
            i += 1

        for num, values in facturations.items():
            print "Facturation : %s" % num
            print "Nb factures : %d" % len(values['factures'])
            print "Nb actes : %d" % len(values['actes'])

        #Facturation : 132
        #Nb factures : 280
        #Nb actes : 517

        #Facturation : 133
        #Nb factures : 182
        #Nb actes : 292

        author = User.objects.get(pk=1)

        # Commencer par péter toutes les healthcare existantes
        CmppHealthCareDiagnostic.objects.all().delete()
        CmppHealthCareTreatment.objects.all().delete()
        # Creation des Healthcare
        HcDiags = []
        HcTraits = []
        for patient_id, pcs in histo.items():
            patient = None
            try:
                patient = PatientRecord.objects.get(old_id=patient_id, service=service)
            except:
                print 'Patient %s non trouve' % patient_id
                continue
            for pc in pcs:
                start_date = _to_date(pc['periode']['date_debut'])
                request_date = _to_date(pc['periode']['date_demande'])
                agree_date = _to_date(pc['periode']['date_accord'])
                insist_date = _to_date(pc['periode']['date_relance'])
                act_number = _to_int(pc['periode']['nbr_seances']) or 0
                if pc['type'] == '1':
                    hc = CmppHealthCareDiagnostic(start_date=start_date,
                        request_date=request_date,
                        agree_date=agree_date,
                        insist_date=insist_date,
                        patient=patient,
                        act_number=act_number,
                        author=author)
                    HcDiags.append(hc)
                else:
                    hc = CmppHealthCareTreatment(start_date=start_date,
                        request_date=request_date,
                        agree_date=agree_date,
                        insist_date=insist_date,
                        patient=patient,
                        act_number=act_number,
                        author=author)
                    HcTraits.append(hc)
                hc.save()
                pc['hc'] = hc
        #CmppHealthCareDiagnostic.objects.bulk_create(HcDiags)
        #CmppHealthCareTreatment.objects.bulk_create(HcTraits)
        # Association des actes au healthcare
        for patient_id, pcs in histo.items():
            patient = None
            try:
                patient = PatientRecord.objects.get(old_id=patient_id, service=service)
            except:
                print 'Patient %s non trouve' % patient_id
                continue
            for pc in pcs:
                hc = pc['hc']
                for act in pc['actes']:
                    a = None
                    try:
                        a = Act.objects.get(old_id=act['id'])
                    except:
                        print "Acte non trouve %s" % act['id']
                        continue
                    if not a.is_billed:
                        print "Acte deja pris en charge mais non facture %s" %a
                        a.is_billed = True
                    a.healthcare = hc
                    a.save()
        # Historique des dossiers, Automatic switch state ? Automated hc creation ?

#            date_accueil = None
#            date_diagnostic = None
#            date_traitement = None
#            date_clos = None
#            date_bilan = None
#            date_suivi = None
#            date_surveillance = None
#            date_retour = None
#            fss = []
#            date_accueil = _to_date(dossier['con_date'])
#            date_traitement = _to_date(dossier['ins_date'])
#            date_clos = _to_date(dossier['sor_date'])
#            if not (date_accueil or date_traitement or date_clos):
#                # no state date, the record is inconsistent
#                writer2.writerow([dossier[c].encode('utf-8') for c in d_cols] + [service.name, 'Non', "Aucune date d'état existante"])
#                continue
#            # Manage states
#            if date_accueil and date_traitement and date_accueil >= date_traitement:
#                date_accueil = None
#            if date_traitement and date_clos and date_traitement >= date_clos:
#                date_traitement = None
#            if date_accueil and date_clos and date_accueil >= date_clos:
#                date_accueil = None
#            if "SESSAD" in service.name:
#                # Il n'y a jamais eu de retour au SESSADs
#                if date_accueil:
#                    fss.append((status_accueil, date_accueil, None))
#                if date_traitement:
#                    fss.append((status_traitement, date_traitement, None))
#                if date_clos:
#                    fss.append((status_clos, date_clos, None))
#            # Jamais de motif et provenance au retour
#            elif service.name == 'CAMSP':
#                date_retour = _to_date(dossier['ret_date'])
#                if date_accueil:
#                    fss.append((status_accueil, date_accueil, None))
#                if not date_retour:
#                    if date_traitement:
#                        s = status_bilan
#                        if dossier['suivi'] == '3':
#                            s = status_suivi
#                        elif dossier['suivi'] == '4':
#                            s = status_surveillance
##                        fss.append((s, date_traitement, "Il peut y avoir plusieurs états de suivi durant cette période de suivi mais ils ne peuvent être déterminés."))
#                        fss.append((s, date_traitement, ""))
#                else:
#                    # Le retour supprime la précédente de clôture, on choisit le retour à j-1
#                    if date_traitement:
#                        # c'est l'inscription
#                        if date_traitement < date_retour:
#                            fss.append((status_suivi, date_traitement, "Etat de traitement indéterminé (Suivi par défaut)."))
#                        old_clos_date = date_retour + relativedelta(days=-1)
#                        fss.append((status_clos, old_clos_date, "La date de clôture est indéterminée (par défaut positionnée à 1 jour avant le retour)."))
#                        s = status_bilan
#                        if dossier['suivi'] == '3':
#                            s = status_suivi
#                        elif dossier['suivi'] == '4':
#                            s = status_surveillance
##                        fss.append((s, date_retour,  "Il peut y avoir plusieurs états de suivi durant cette période de suivi mais ils ne peuvent être déterminés."))
#                        fss.append((s, date_retour,  ""))
#                if date_clos:
#                    if date_retour and date_clos < date_retour:
#                        print 'La date de clôture ne peut être antérieure à la date de retour!'
#                    else:
#                        fss.append((status_clos, date_clos, None))
#            else:
#                date_retour = _to_date(dossier['ret_date'])
#                if date_accueil:
#                    fss.append((status_accueil, date_accueil, None))
#                if date_traitement:
#                    fss.append((status_diagnostic, date_traitement, "Inscription en diag mais pourrait etre en trait. A préciser"))
#                if (date_retour and date_clos and date_retour > date_clos) or not date_clos:
#                    if old_id in tables_data['pcs'].keys():
#                        pcs = tables_data['pcs'][old_id]
#                        last_pc = pcs[len(pcs)-1]
#                        if last_pc['genre_pc'] == '2':
#                            status, date, msg = fss[len(fss)-1]
#                            last_date = date + relativedelta(days=1)
#                            fss.append((status_traitement, last_date, "Date à préciser."))
#                else:
#                    fss.append((status_clos, date_clos, None))

        print "<-- Terminé"
    print "====== Fin à %s ======" % str(datetime.today())


if __name__ == "__main__":
    import_dossiers_phase_1()
