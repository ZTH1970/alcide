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
from calebasse.dossiers.models import PatientRecord, Status, FileState, PatientAddress, PatientContact
from calebasse.ressources.models import Service
from calebasse.personnes.models import Worker, Holiday, ExternalWorker, ExternalTherapist
from calebasse.ressources.models import (WorkerType, ParentalAuthorityType, ParentalCustodyType,
    FamilySituationType, TransportType, TransportCompany, Provenance, AnalyseMotive, FamilyMotive,
    CodeCFTMEA, SocialisationDuration, School, SchoolLevel, OutMotive, OutTo, AdviceGiver,
    MaritalStatusType, Job, PatientRelatedLink)

# Configuration
db_path = "./scripts/20130104-213225"

#dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
dbs = ["F_ST_ETIENNE_SESSAD_TED"]


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

# Mettre tous les actes avant le 3 janvier à validation_locked = True
# Mettre tous les actes avec dossier['marque'] = 1 à is_billed = True




#tarifs: prix_journee.csv

#Contacts et données secu, assuré
#Adresses
#prise en charges (cmpp)
#Quel contact est l'assuré ? voir pc Idem, la caisse est pas sur le contact mais sur la pc!
#Les états des dossiers!
#diag id = 1 trait id = 2
#notes ?

#Ajouter au contact lien avec l'enfant mère, grand mèere, etc.
#table parente champs du dossier: parente.csv associé à la table contact ?
#Ajouter au contact
#Attention caisse il faut les ancien id pour retourber? on peut rechercher sur le numéro de la caisse!


#tables = ["dossiers", "adresses", "contacts", "convocations", "dossiers_ecole", "dossiers_mises", "pc", "periodes_pc","pmt", "rm", , "sor_motifs", "sor_orientation", "suivi"]
#tables = ["dossiers_test"]

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


def main():
    """ """
    print "====== Début à %s ======" % str(datetime.today())

    f1 = open('./scripts/dossiers_ecoles_manuel.csv', 'wb')
    writer1 = csv.writer(f1, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    f2 = open('./scripts/dossiers_manuel.csv', 'wb')
    writer2 = csv.writer(f2, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    f3 = open('./scripts/contacts_manuel.csv', 'wb')
    writer3 = csv.writer(f3, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

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

        print "--> Lecture table des dossiers..."
        csvfile = open(os.path.join(db_path, db, 'dossiers.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        d_cols = csvlines.next()
        writer2.writerow(d_cols + ['service', 'creation', 'commenataire'])
        tables_data['dossiers'] = []
        for line in csvlines:
            #Au moins nom et prénom
            if _exist(line[1]) and _exist(line[2]):
                data = _get_dict(d_cols, line)
                tables_data['dossiers'].append(data)
            else:
                writer2.writerow(line + [service.name, 'Non', 'Ni Nom, ni prénom'])
        csvfile.close()
        print "<-- Terminé"

        print "--> Chargement mises..."
        mises = {}
        csvfile = open(os.path.join(db_path, db, 'mises.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        for line in csvlines:
            mises[line[0]] = (line[1], line[2])
        csvfile.close()
        print "<-- Terminé"

        print "--> Chargement quotations..."
        mises_per_patient = {}
        csvfile = open(os.path.join(db_path, db, 'dossiers_mises.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        for line in csvlines:
            code, axe = mises[line[2]]
            quotation = CodeCFTMEA.objects.get(code=int(code), axe=int(axe))
            if line[1] in mises_per_patient.keys():
                mises_per_patient[line[1]].append(quotation)
            else:
                mises_per_patient[line[1]] = [quotation]
        csvfile.close()
        print "<-- Terminé"

        print "--> Ajout périodes de socialisation..."
        social_duration_per_patient = {}
        csvfile = open(os.path.join(db_path, db, 'dossiers_ecoles.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        writer1.writerow(cols + ['service'])
        i = 0
        for line in csvlines:
            i += 1
        print "Nombre à traiter : %d" % i
        csvfile.close()
        csvfile = open(os.path.join(db_path, db, 'dossiers_ecoles.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        csvlines.next()
        for line in csvlines:
            school = None
            if _exist(line[2]):
                school = School.objects.get(old_id=line[2], old_service=service.name)
            level = None
            try:
                level = SchoolLevel.objects.get(old_id=line[4], old_service=service.name)
            except:
                pass
            contact = line[3]
            if contact != "":
                contact += ' ' + line[7]
            else:
                contact = line[7]
            start_date = _to_date(line[5])
            social_duration = SocialisationDuration(school=school, level=level, start_date=start_date, contact=contact)
            social_duration.save()
            if line[1] in social_duration_per_patient.keys():
                social_duration_per_patient[line[1]].append(social_duration)
            else:
                social_duration_per_patient[line[1]] = [social_duration]
            #Produce file for manuel treatment:
            for j in range(6, 16):
                if j != 7 and _exist(line[j]):
                    writer1.writerow(line + [service.name])
            i -= 1
            if not (i % 10):
                sys.stdout.write('%d' %i)
            else:
                sys.stdout.write('.')
            sys.stdout.flush()
        csvfile.close()
        print "<-- Terminé"

        print "--> Ajout des adresses..."
        adresses_per_patient = {}
        adresses_per_old_id = {}
        csvfile = open(os.path.join(db_path, db, 'adresses.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        i = 0
        for line in csvlines:
            i += 1
        print "Nombre à traiter : %d" % i
        csvfile.close()
        csvfile = open(os.path.join(db_path, db, 'adresses.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        csvlines.next()
        for line in csvlines:
            phone = extract_phone(line[5])
            comment = ''
            if _exist(line[10]):
                comment += line[10] + ' - '
            if _exist(line[5]):
                comment += "Numéro 1 : " + line[5] + ' - '
            if _exist(line[8]):
                comment += "Numéro 2 : " + line[8] + ' - '
            fax = None
            place_of_life = False
            if _exist(line[9]) and line[9] == '-1':
                place_of_life = True
            number = None
            street = line[11]
            address_complement = line[12]
            zip_code = None
            if _exist(line[3]):
                if len(line[3]) > 5:
                    zip_code = line[3][-5:]
                else:
                    zip_code = line[3]
            city = line[4]

            address = PatientAddress(phone=phone, comment=comment,
                fax=fax, place_of_life=place_of_life, number=number,
                street=street, address_complement=address_complement,
                zip_code=zip_code, city=city)

            address.save()
            if line[1] in adresses_per_patient.keys():
                adresses_per_patient[line[1]].append(address)
            else:
                adresses_per_patient[line[1]] = [address]
            adresses_per_old_id[line[0]] = (address, line[1])
            i -= 1
            if not (i % 10):
                sys.stdout.write('%d' %i)
            else:
                sys.stdout.write('.')
            sys.stdout.flush()
        csvfile.close()
        print "<-- Terminé"

        print "--> Chargement des prise en charge pour le CMPP..."
        print "<-- Terminé"

        print "--> Ajout des contacts..."
        contacts_per_patient = {}
        csvfile = open(os.path.join(db_path, db, 'contacts.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        writer3.writerow(cols + ['service', 'commentaire'])
        i = 0
        for line in csvlines:
            i += 1
        print "Nombre à traiter : %d" % i
        csvfile.close()
        csvfile = open(os.path.join(db_path, db, 'contacts.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        csvlines.next()
        for line in csvlines:
            phone = extract_phone(line[13])
            mobile = extract_phone(line[14])
            contact_comment = ''
            if _exist(line[13]):
                contact_comment += "Travail : " + line[13] + ' - '
            if _exist(line[14]):
                contact_comment += "Mobile : " + line[14] + ' - '
            if _exist(line[17]):
                contact_comment += "Divers : " + line[17] + ' - '
            last_name = treat_name(line[3])
            first_name = treat_name(line[4])
            gender = None
            if line[2] == "1":
                gender = 1
            if line[2] == "2":
                gender = 2
            email = None
            if _exist(line[15]):
                email = line[15]
            birthplace = None
            if _exist(line[6]):
                birthplace = line[6]
            social_security_id = get_nir(line[7], line[8], writer3, line, service)
            if social_security_id == -1:
                msg = 'Numéro %s de longueur diff de 13.' % line[7]
                writer3.writerow(line + [service.name, msg])
                contact_comment += "Numéro NIR invalide : " + line[7] + ' - '
                social_security_id = None
            birthdate = _to_date(line[5])
            job = get_job(service, line[9])
            parente = None
            try:
                if service.name == 'CAMSP':
                    parente = PatientRelatedLink.objects.get(old_camsp_id=_to_int(line[11]))
                elif service.name == 'CMPP':
                    parente = PatientRelatedLink.objects.get(old_cmpp_id=_to_int(line[11]))
                elif service.name == 'SESSAD DYS':
                    parente = PatientRelatedLink.objects.get(old_sessad_dys_id=_to_int(line[11]))
                elif service.name == 'SESSAD TED':
                    parente = PatientRelatedLink.objects.get(old_sessad_ted_id=_to_int(line[11]))
            except:
                pass
            twinning_rank = None
            thirdparty_payer = False
            begin_rights = None
            end_rights = None
            health_center = None

            contact = PatientContact(phone=phone, mobile= mobile,
                contact_comment=contact_comment,
                last_name = last_name, first_name = first_name,
                gender = gender, email = email, parente = parente,
                social_security_id = social_security_id,
                birthdate = birthdate, job = job, birthplace=birthplace,
                twinning_rank = twinning_rank,
                thirdparty_payer = thirdparty_payer,
                begin_rights = begin_rights,
                end_rights = end_rights,
                health_center = health_center)
            contact.save()

            if not line[1] in adresses_per_old_id:
                msg = 'Contact sans adresse'
                writer3.writerow(line + [service.name, msg])
                contact.delete()
            else:
                adresse, old_patient_id = adresses_per_old_id[line[1]]
                contact.addresses.add(adresse)
                # Ajouter l'adresse au contact
                # Faire une liste des contacts par patient pour ajouter ensuite
                if old_patient_id in contacts_per_patient.keys():
                    contacts_per_patient[old_patient_id].append(contact)
                else:
                    contacts_per_patient[old_patient_id] = [contact]
            i -= 1
            if not (i % 10):
                sys.stdout.write('%d' %i)
            else:
                sys.stdout.write('.')
            sys.stdout.flush()
        csvfile.close()
        print "<-- Terminé"

        print "--> Ajout dossiers..."
        print "Nombre à traiter : %d" % len(tables_data['dossiers'])
        i = len(tables_data['dossiers'])
        for dossier in tables_data['dossiers']:

            date_accueil = None
            date_diagnostic = None
            date_traitement = None
            date_clos = None
            date_bilan = None
            date_suivi = None
            date_surveillance = None
            date_retour = None
            fss = []
            date_accueil = _to_date(dossier['con_date'])
            date_traitement = _to_date(dossier['ins_date'])
            date_clos = _to_date(dossier['sor_date'])
            if not (date_accueil or date_traitement or date_clos):
                # no state date, the record is inconsistent
                writer2.writerow([dossier[c].encode('utf-8') for c in d_cols] + [service.name, 'Non', "Aucune date d'état existante"])
                continue
            # Manage states
            if date_accueil and date_traitement and date_accueil > date_traitement:
                date_accueil = None
            if date_traitement and date_clos and date_traitement > date_clos:
                date_traitement = None
            if date_accueil and date_clos and date_accueil > date_clos:
                date_accueil = None
            if "SESSAD" in service.name:
                # Il n'y a jamais eu de retour au SESSADs
                if date_accueil:
                    fss.append((status_accueil, date_accueil, None))
                if date_traitement:
                    fss.append((status_traitement, date_traitement, None))
                if date_clos:
                    fss.append((status_clos, date_clos, None))
            # Jamais de motif et provenance au retour
            elif service.name == 'CAMSP':
                date_retour = _to_date(dossier['ret_date'])
                if date_accueil:
                    fss.append((status_accueil, date_accueil, None))
                if not date_retour:
                    if date_traitement:
                        s = status_bilan
                        if dossier['suivi'] == '3':
                            s = status_suivi
                        elif dossier['suivi'] == '4':
                            s = status_surveillance
                        fss.append((s, date_traitement, "Il peut y avoir plusieurs états de suivi durant cette période de suivi mais ils ne peuvent être déterminés."))
                else:
                    # Le retour supprime la précédente de clôture, on choisit le retour à j-1
                    if date_traitement:
                        # c'est l'inscription
                        if date_traitement < date_retour:
                            fss.append((status_suivi, date_traitement, "Etat de traitement indéterminé (Suivi par défaut)."))
                        old_clos_date = date_retour + relativedelta(days=-1)
                        fss.append((status_clos, old_clos_date, "La date de clôture est indéterminée (par défaut positionnée à 1 jour avant le retour)."))
                        s = status_bilan
                        if dossier['suivi'] == '3':
                            s = status_suivi
                        elif dossier['suivi'] == '4':
                            s = status_surveillance
                        fss.append((s, date_retour,  "Il peut y avoir plusieurs états de suivi durant cette période de suivi mais ils ne peuvent être déterminés."))
                if date_clos:
                    if date_retour and date_clos < date_retour:
                        print 'La date de clôture ne peut être antérieure à la date de fermeture!'
                    else:
                        fss.append((status_clos, date_clos, None))

            else:
                pass
                # date_traitement c'est diagnostic ou traitement
                # CMPP : Si retour ret_diag = -1 si retour en diag.
                # Pour savoir si c'est traitement ou diagnostique il faut connaître les actes validés passés
                # Donc cela ne peut être fait que lorsque l'import des actes seront effectués et que l'on sera comment ils sont pris en charge
                # Donc on run ce script, on run l'import des rdv patients et actes, puis un script pour mettre à jour les états et imputer les actes facturés aux pc
                # L'import des pc ne peut aussi se faire qu'après l'import des actes
                # imports des actes dit ce qui a été facturé sans le détail de quelle facture ou quel invoice.
                # à l'import, tous les actes 2012 seront locked, jedui et vendredi seront à faire à la main par les secrétaires
                # pour le camsp et sessads, on prendre à partir de 2013 les actes
                # pour le cmpp, il va faloire imputer tous les actes facturés aux prises en charges
                # pour savoir dans la nouvelle facturation (134) comment les imputer et donc savoir dans quel état est le dossier

            for col in ('mdph', 'code_archive', 'aeeh', 'mdph_departement', 'pps', 'pps_deb', 'pps_fin', 'mdph_Debut', 'mdph_Fin'):
                if _exist(dossier[col]):
                    writer2.writerow([dossier[c].encode('utf-8') for c in d_cols] + [service.name, 'Oui', "Données présentes non traitées"])
                    break

            #People
            first_name = treat_name(dossier['prenom'])
            last_name = treat_name(dossier['nom'])
            display_name = None
            gender = _to_int(dossier['nais_sexe'])
            if not gender in (1,2):
                gender = None
            email = None
            phone = None

            #PatientContact
            mobile = None
            social_security_id = None
            birthdate = _to_date(dossier['nais_date'])
            twinning_rank = _to_int(dossier['nais_rang'])
            # Pourra etre init à l'import des contacts après création du dossier
            thirdparty_payer = False
            begin_rights = None
            end_rights = None
            health_center = None
            addresses = None
            contact_comment = None

            #PatientRecord
            creator = creator
            # Pourra etre init à l'import des contacts après création du dossier
            nationality = None
            paper_id = None
            comment = dossier['infos']
            pause = False
            if _exist(dossier['blocage']):
                pause = True
            confidential = False
            if _exist(dossier['non_communication_ecole']):
                confidential = True

            # Physiology and health data
            size = _to_int(dossier['taille'])
            weight = _to_int(dossier['poids'])
            pregnancy_term = _to_int(dossier['terme'])
            cranium_perimeter = None
            chest_perimeter = None
            apgar_score_one = _to_int(dossier['apgar_1'])
            apgar_score_two = _to_int(dossier['apgar_5'])


            # Inscription motive
            # Up to now only used at the CAMSP
            analysemotive = None
            try:
                analysemotive = AnalyseMotive.objects.get(id=_to_int(dossier['ins_motif']))
            except:
                pass
            # Up to now only used at the CAMSP
            familymotive = None
            try:
                familymotive = FamilyMotive.objects.get(id=_to_int(dossier['ins_motif_exprim']))
            except:
                pass
            provenance = None
            try:
                provenance = Provenance.objects.get(old_id=_to_int(dossier['ins_provenance']), old_service=service.name)
            except:
                pass
            # Up to now only used at the CAMSP
            advicegiver = None
            try:
                advicegiver = AdviceGiver.objects.get(id=_to_int(dossier['con_qui']))
            except:
                pass

            # Inscription motive
            # Up to now only used at the CAMSP
            outmotive = None
            try:
                outmotive = OutMotive.objects.get(id=_to_int(dossier['sor_motif']))
            except:
                pass
            # Up to now only used at the CAMSP
            outto = None
            try:
                outto = OutTo.objects.get(id=_to_int(dossier['sor_orientation']))
            except:
                pass

            # Family
            sibship_place = _to_int(dossier['nais_fratrie'])
            nb_children_family = _to_int(dossier['nbr_enfants'])
            parental_authority = None
            try:
                parental_authority = ParentalAuthorityType.objects.get(id=_to_int(dossier['autorite_parentale']))
            except:
                pass
            # Up to now only used at the CAMSP
            family_situation = None
            try:
                family_situation = FamilySituationType.objects.get(id=_to_int(dossier['situation_familiale']))
            except:
                pass
            # Up to now only used at the CAMSP
            child_custody = None
            try:
                child_custody = ParentalCustodyType.objects.get(id=_to_int(dossier['garde']))
            except:
                pass

            rm_mother = get_rm(service, dossier['rm_mere'])
            rm_father = get_rm(service, dossier['rm_pere'])
            job_mother = get_job(service, dossier['prof_mere'])
            job_father = get_job(service, dossier['prof_pere'])
            family_comment = None

            # Transport
            transportcompany = None
            try:
                if service.name == 'CAMSP':
                    transportcompany = TransportCompany.objects.get(old_camsp_id=_to_int(dossier['transport']))
                elif service.name == 'CMPP':
                    transportcompany = TransportCompany.objects.get(old_cmpp_id=_to_int(dossier['transport']))
                elif service.name == 'SESSAD DYS':
                    transportcompany = TransportCompany.objects.get(old_sessad_dys_id=_to_int(dossier['transport']))
                elif service.name == 'SESSAD TED':
                    transportcompany = TransportCompany.objects.get(old_sessad_ted_id=_to_int(dossier['transport']))
            except:
                pass
            transporttype = None
            try:
                transporttype = TransportType.objects.get(id=_to_int(dossier['type_transport']))
            except:
                pass

            # FollowUp
            externaldoctor = None
            try:
                externaldoctor = ExternalTherapist.objects.get(old_id=_to_int(dossier['medecin_exterieur']), old_service=service.name)
            except:
                pass
            externalintervener = None
            try:
                externalintervener = ExternalWorker.objects.get(old_id=_to_int(dossier['intervenant_exterieur']), old_service=service.name)
            except:
                pass

            old_id = dossier['id']
            old_old_id = dossier['ancien_numero']


            patient, created = PatientRecord.objects.get_or_create(first_name = first_name,
                    last_name = last_name,
                    birthdate = birthdate,
                    twinning_rank = twinning_rank,
                    gender = gender,
                    display_name = display_name,
                    email = email,
                    phone = phone,
                    mobile = mobile,
                    contact_comment = contact_comment,
                    nationality = nationality,
                    paper_id = paper_id,
                    comment = comment,
                    pause = pause,
                    confidential = confidential,
                    size = size,
                    weight = weight,
                    pregnancy_term = pregnancy_term,
                    cranium_perimeter = cranium_perimeter,
                    chest_perimeter = chest_perimeter,
                    apgar_score_one = apgar_score_one,
                    apgar_score_two = apgar_score_two,
                    analysemotive = analysemotive,
                    familymotive = familymotive,
                    provenance = provenance,
                    advicegiver = advicegiver,
                    outmotive = outmotive,
                    outto = outto,
                    sibship_place = sibship_place,
                    nb_children_family = nb_children_family,
                    parental_authority = parental_authority,
                    family_situation = family_situation,
                    rm_mother = rm_mother,
                    rm_father = rm_father,
                    job_mother = job_mother,
                    job_father = job_father,
                    family_comment = family_comment,
                    child_custody = child_custody,
                    transportcompany = transportcompany,
                    transporttype = transporttype,
                    externaldoctor = externaldoctor,
                    externalintervener = externalintervener,
                    service=service,
                    creator=creator,
                    old_id = old_id,
                    old_old_id = old_old_id)

#            if created:
#                print 'Creation de%s' % patient
#            else:
#                print 'Patient %s existe' % patient

            # Init states
            if service.name != 'CMPP':
                if not fss:
                    print "Pas d'etat et le dossier patient %s (old_id) a ete cree!" % old_id
                else:
                    fs = FileState(status=fss[0][0], author=creator, previous_state=None)
                    date_selected = fss[0][1]
                    fs.patient = patient
                    fs.date_selected = date_selected
                    fs.comment = fss[0][2]
                    fs.save()
                    patient.last_state = fs
                    patient.save()
                    if len(fss) > 1:
                        for status, date, comment in fss[1:]:
                            patient.set_state(status=status, author=creator, date_selected=date, comment=comment)

            if old_id in mises_per_patient.keys():
                for quotation in mises_per_patient[old_id]:
                    if quotation.axe == 1:
                        patient.mises_1.add(quotation)
                    elif quotation.axe == 2:
                        patient.mises_2.add(quotation)
                    elif quotation.axe == 3:
                        patient.mises_3.add(quotation)
                    else:
                        raise

            if old_id in social_duration_per_patient.keys():
                for social_duration in social_duration_per_patient[old_id]:
                    patient.socialisation_durations.add(social_duration)

            for t_the in ('the_medecin', 'the_referent', 'the_therapeute'):
                try:
                    therapist = None
                    if service.name == 'CAMSP':
                        therapist = Worker.objects.get(old_camsp_id=_to_int(dossier[t_the]))
                    elif service.name == 'CMPP':
                        therapist = Worker.objects.get(old_cmpp_id=_to_int(dossier[t_the]))
                    elif service.name == 'SESSAD DYS':
                        therapist = Worker.objects.get(old_sessad_dys_id=_to_int(dossier[t_the]))
                    elif service.name == 'SESSAD TED':
                        therapist = Worker.objects.get(old_sessad_ted_id=_to_int(dossier[t_the]))
                    patient.coordinators.add(therapist)
                except:
                    pass

            # Initialisation adresses et contacts
            if old_id in adresses_per_patient.keys():
                for adresse in adresses_per_patient[old_id]:
                    patient.addresses.add(adresse)
            if old_id in contacts_per_patient.keys():
                for contact in contacts_per_patient[old_id]:
                    if contact.last_name == patient.last_name \
                            and contact.first_name == patient.first_name:
#                        print "Le contact %s %s est le patient" % (contact.last_name, contact.first_name)
                        if not patient.birthdate:
                             patient.birthdate = contact.birthdate
                        patient.birthplace = contact.birthplace
                        patient.email = contact.email
                        patient.phone = contact.phone
                        patient.mobile = contact.mobile
                        patient.social_security_id = contact.social_security_id
                        patient.thirdparty_payer = contact.thirdparty_payer
                        patient.begin_rights = contact.begin_rights
                        patient.end_rights = contact.end_rights
                        patient.health_center = contact.health_center
                        patient.contact_comment = contact.contact_comment
                        patient.save()
                        contact.delete()
                    else:
                        patient.contacts.add(contact)

            #Etat des dossiers

            # patient.policyholder soit le contact, d'il n'y en a qu'un
            # au cmmp, cf la pc

            # Dossier en pause facturation! champs pause sur le dossier OK
            # si aucun contact, ou aucun contact avec un Nir valide!

            #Tiers-payant ? healthcenter ?

            # Notifications au sessad, il n'y en a pas!

#            i += 1
#            print 'Fin de traitement pour le dossier %s' % patient
#            if i >= 10:
#                break
            i -= 1
            if not (i % 10):
                sys.stdout.write('%d' %i)
            else:
                sys.stdout.write('.')
            sys.stdout.flush()

        print "<-- Terminé"
    print "====== Fin à %s ======" % str(datetime.today())

            #Travail manuel pour secreatires
#            mdph_requests = models.ManyToManyField('ressources.MDPHRequest',
#            mdph_responses = models.ManyToManyField('ressources.MDPHResponse',


#            policyholder = None
#            contacts = None


if __name__ == "__main__":
    main()
