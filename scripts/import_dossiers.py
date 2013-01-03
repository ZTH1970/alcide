# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys
import csv

from datetime import datetime, time

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
db_path = "./scripts/20121221-192258"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
#dbs = ["F_ST_ETIENNE_CMPP"]



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


def _get_dict(cols, line):
    """"""
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res

tables_data = {}

map_rm_camsp = [1, 3, 2, 8, 6, 4]

def get_rm(service, val):
    old_id_rm = _to_int(val)
    if old_id_rm < 1 or 'SESSAD' in service.name:
        return None
    if service.name == 'CAMSP':
        old_id_rm = map_rm_camsp[old_id_rm - 1]
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
    if service.name == 'CAMSP' and old_id_job == 25:
        return None
    if service.name == 'CAMSP':
        old_id_job = map_job_camsp[old_id_job - 1]
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
    try:
        nir = int(nir)
    except:
        return -2
    if key:
        try:
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
        writer2.writerow(d_cols + ['service', 'creation'])
        tables_data['dossiers'] = []
        for line in csvlines:
            #Au moins nom et prénom
            if _exist(line[1]) and _exist(line[2]):
                data = _get_dict(d_cols, line)
                tables_data['dossiers'].append(data)
            else:
                writer2.writerow(line + [service.name, 'Non'])
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
            if _exist(line[9]) and line[9] != '-1':
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
            social_security_id = get_nir(line[7], line[8], writer3, line, service)
            if social_security_id == -1:
                msg = 'Numéro %s de longueur diff de 13.' % line[7]
                writer3.writerow(line + [service.name, msg])
                contact_comment += "Numéro NIR invalide : " + line[7] + ' - '
                social_security_id = None
            if social_security_id == -1:
                msg = 'Impossible de convertir numéro %s.' % line[7]
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
                birthdate = birthdate, job = job,
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



        accueil_status = Status.objects.filter(type="ACCUEIL").filter(services=service)
        creator = User.objects.get(id=1)

        print "--> Ajout dossiers..."
        print "Nombre à traiter : %d" % len(tables_data['dossiers'])
        i = len(tables_data['dossiers'])
        for dossier in tables_data['dossiers']:
            for col in ('mdph', 'code_archive', 'aeeh', 'mdph_departement', 'pps', 'pps_deb', 'pps_fin', 'mdph_Debut', 'mdph_Fin'):
                if _exist(dossier[col]):
                    writer2.writerow([dossier[c].encode('utf-8') for c in d_cols] + [service.name, 'Oui'])

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

            fs = FileState(status=accueil_status[0], author=creator, previous_state=None)
            "Date du premier contact"
            date_selected = None
            if not date_selected:
                date_selected = patient.created
            fs.patient = patient
            fs.date_selected = date_selected
            fs.save()
            patient.last_state = fs
            patient.save()

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
                    #Et quand le contact est le patient ? reconnaissance nom et prénom!
                    if contact.last_name == patient.last_name \
                            and contact.first_name == patient.first_name:
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


            # L'assuré c'est le premier contact sauf au CMPP où c'est celui déclaré sur la dernière pc s'il existe

            # Dossier en pause facturation! champs pause sur le dossier OK
            # si aucun contact, ou aucun contact avec un Nir valide!

            #Tiers-payant ? healthcenter ?

            #Etat des dossiers

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
