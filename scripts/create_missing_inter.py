# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv
import codecs
import string
import random
from datetime import datetime, time

import django.core.management
import alcide.settings
django.core.management.setup_environ(alcide.settings)

from django.contrib.auth.models import User
from alcide.actes.models import EventAct
from alcide.agenda.models import Event, EventType
from alcide.dossiers.models import PatientRecord, Status, FileState
from alcide.ressources.models import Service
from alcide.personnes.models import Worker, Holiday, UserWorker
from alcide.ressources.models import WorkerType


f_inter = "./scripts/recup_intervenants.csv"

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

from django.db import transaction

@transaction.commit_manually
def main():
    print datetime.now()
    '''User and worker'''
    cmpp = Service.objects.get(name="CMPP")
    camsp = Service.objects.get(name="CAMSP")
    sessad_ted = Service.objects.get(name="SESSAD TED")
    sessad_dys = Service.objects.get(name="SESSAD DYS")

    type_stagiaire = WorkerType.objects.get(pk=21)
    type_ortho_lib = WorkerType.objects.get(pk=22)

    print "--> Chargement des intervenants..."
    csvfile = open(f_inter, 'rb')
    csvlines = UnicodeReader(csvfile, delimiter=';', quotechar='|',encoding='utf-8')
    csvlines.next()
    cols = csvlines.next()
    intervenants = []
    for line in csvlines:
        data = _get_dict(pc_cols, line)
        intervenants.append(data)
    csvfile.close()
    print "<-- Terminé"

    for intervenant in intervenants:
        is_user = False
        if intervenant['Pk type'] == '21':
            is_user = True

        user = None
        if is_user:
            username = intervenant['prenom'][0].lower() + intervenant['nom'].lower()
            digits = rdm_str = ''.join(random.choice(string.digits) for x in range(4))
            passwd = intervenant['prenom'][0].lower() + intervenant['nom'][0].lower() + digits
            user = User(username=username)
            user.set_password(passwd)
            user.save()

        last_name = intervenant['nom']
        first_name = intervenant['prenom']
        type = None
        if intervenant['Pk type'] == '21':
            type = type_stagiaire
        else:
            type = type_ortho_lib
        enabled = True
        old_camsp_id = intervenant['old_camsp_id']
        old_cmpp_id = intervenant['old_cmpp_id']
        old_sessad_dys_id = intervenant['old_sessad_dys_id']
        old_sessad_ted_id = intervenant['old_sessad_ted_id']

        worker = Worker(last_name=last_name, first_name=first_name,
            type=type,
            old_camsp_id=old_camsp_id, old_cmpp_id=old_cmpp_id,
            old_sessad_dys_id=old_sessad_dys_id, old_sessad_ted_id=old_sessad_ted_id,
            enabled=enabled)
        worker.save()
        if old_camsp_id and old_camsp_id != '':
            worker.services.add(camsp)
        if old_cmpp_id and old_cmpp_id != '':
            worker.services.add(cmpp)
        if old_sessad_dys_id and old_sessad_dys_id != '':
            worker.services.add(sessad_dys)
        if old_sessad_ted_id and old_sessad_ted_id != '':
            worker.services.add(sessad_ted)
        worker.save()
        if is_user:
            UserWorker(user=user,worker=worker).save()

        clones = []
#        Worker.objects.get -> recuperer les anciens importés via le old_id dans chaque service
#        Rechercher tous leur events, acts, etc et leur associer au worker cree
#        détruire les clones
#        Ecrire dans un fichier les logins et password des stagiaires


    transaction.commit()
    print datetime.now()

if __name__ == "__main__":
    main()
