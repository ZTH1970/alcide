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
from calebasse.dossiers.models import PatientRecord, Status, FileState
from calebasse.ressources.models import Service
from calebasse.personnes.models import Worker, Holiday, ExternalWorker, ExternalTherapist
from calebasse.ressources.models import (WorkerType, ParentalAuthorityType, ParentalCustodyType,
    FamilySituationType, TransportType, TransportCompany, Provenance, AnalyseMotive, FamilyMotive,
    CodeCFTMEA, SocialisationDuration, School, SchoolLevel, OutMotive, OutTo)

# Configuration
db_path = "./scripts/20121221-192258"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]
#dbs = ["F_ST_ETIENNE_CMPP"]



#tarifs: prix_journee.csv

#Contacts et données secu, assuré
#Adresses
#prise en charges (cmpp)
#état des dossiers

#Croiser, dans le dossier patient: prof mere et mere or nous on veut le mettre sur les contacts
#Notes, si existe mettre en description, mais tous les fichiers vides ?
#Les états des dossiers!


#les contacts sont des people qui apparaissent dans les listes des exterieurs ?
#diag id = 1 trait id = 2
#notes ?

#Ajouter au contact lien avec l'enfant mère, grand mèere, etc.
#table parente champs du dossier: parente.csv associé à la table contact ?
#Ajouter au contact: catégorie socio pro
#Import csp.csv
#Imports adresses et contacts
#Quel contact est l'assuré ?
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

def main():
    """ """
    print "====== Début à %s ======" % str(datetime.today())

    f1 = open('./scripts/dossiers_ecoles_manuel.csv', 'wb')
    writer1 = csv.writer(f1, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    f2 = open('./scripts/dossiers_manuel.csv', 'wb')
    writer2 = csv.writer(f2, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

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
            # Pourra etre init à l'import des contacts après création du dossier
            social_security_id = None
            birthdate = _to_date(dossier['nais_date'])
            twinning_rank = _to_int(dossier['nais_rang'])
            # Pourra etre init à l'import des contacts après création du dossier
            thirdparty_payer = None
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
            #Champs pas trouvé dans le dossier
            advicegiver = None

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

#            i += 1
#            print 'Fin de traitement pour le dossier %s' % patient
#            if i >= 10:
#                break
            i -= 1
            if not (i % 10):
                sys.stdout.write('%d ' %i)
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
