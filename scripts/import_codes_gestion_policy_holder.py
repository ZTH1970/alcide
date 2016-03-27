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
from alcide.ressources.models import Service, ManagementCode
from alcide.personnes.models import Worker, Holiday, ExternalWorker, ExternalTherapist
from alcide.ressources.models import (WorkerType, ParentalAuthorityType, ParentalCustodyType,
    FamilySituationType, TransportType, TransportCompany, Provenance, AnalyseMotive, FamilyMotive,
    CodeCFTMEA, SocialisationDuration, School, SchoolLevel, OutMotive, OutTo, AdviceGiver,
    MaritalStatusType, Job, PatientRelatedLink, HealthCenter)

# Configuration
db_path = "./scripts/20130104-213225"

dbs = ["F_ST_ETIENNE_SESSAD_TED", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD"]

def _get_dict(cols, line):
    """"""
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res


def main():
    """ """
    print "====== Début à %s ======" % str(datetime.today())

    for db in dbs:
        if "F_ST_ETIENNE_CAMSP" == db:
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
        pcs = []
        for line in csvlines:
            data = _get_dict(pc_cols, line)
            pcs.append(data)
        csvfile.close()
        print "<-- Terminé"

        for pc in pcs:
            patient = None
            try:
                #contact = PatientContact.objects.get(old_contact_id=pc['contact_id'])
                #print contact.patientrecord_set.all()
                patient = PatientRecord.objects.get(old_id=pc['enfant_id'], service=service)
            except:
                #print "Contact not found for pc with id %s" %pc['id']
                print "Patient %s not found for pc with id %s" % (pc['enfant_id'], pc['id'])
                # CAMSP : 443, 565, 640, 647
                # SESSAD DYS: 92, 123, 185, 191
            else:
                try:
                    if pc['code_gestion'] and pc['code_gestion'] != '0' :
                        mc = ManagementCode.objects.get(old_id=pc['code_gestion'])
                        print "Init de %s sur ph %s de l'enfant %s" % (str(mc), str(patient.policyholder), str(patient))
                        patient.policyholder.management_code = mc
                        patient.policyholder.save()
                except:
                    print "Management Code Not found, ID : %s" %pc['code_gestion']

    print "====== Fin à %s ======" % str(datetime.today())


if __name__ == "__main__":
    main()
