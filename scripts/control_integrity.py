# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Script de contrôle et de reporting
"""

import os
import tempfile

from datetime import datetime, timedelta
from datetime import date as date_setter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calebasse.settings")

from calebasse.facturation.models import Invoice
from calebasse.actes.models import Act, ValidationMessage
from calebasse.dossiers.models import PatientRecord
from calebasse.agenda.models import EventWithAct

SEND_MAIL = "mates@entrouvert.com"
OUTPUT_DIR = "./"
PREFIX = "analyse"

ANALYSE_SDT = datetime(2013,1,1)

ALWAYS_SEND_MAIL = True

LOOKUP_NEW = True
END_LOOKUP = datetime.today()

SERVICES = ('CMPP', 'CAMSP', 'SESSAD TED', 'SESSAD DYS')
#SERVICES = ('CAMSP',)
#SERVICES = ('CAMSP', 'SESSAD TED', 'SESSAD DYS')
#SERVICES = ('SESSAD DYS',)

QUIET = False

if __name__ == '__main__' :
    prefix = '%s-%s.' % (PREFIX, datetime.utcnow())
    logger_fn = os.path.join(OUTPUT_DIR, prefix + 'log')
    assert not os.path.isfile(logger_fn), 'Analyse log file "%s" already exists' % logger_fn
    logger = tempfile.NamedTemporaryFile(suffix='.logtmp',
            prefix=prefix, dir=OUTPUT_DIR, delete=False)

    logger.write("Script de contôle de Calebasse : %s\n\n" % datetime.utcnow())

    need_mail = False

    if LOOKUP_NEW:
        for service_name in SERVICES:
            for date in [(ANALYSE_SDT + timedelta(days=i)).date() for i in range(0, (END_LOOKUP.date()-ANALYSE_SDT.date()).days)]:
                "Be sure all acts are created in 2014"
                acts = list(Act.objects \
                        .filter(date=date, patient__service__name=service_name) \
                        .select_related() \
                        .prefetch_related('doctors',
                                'patient__patientcontact',
                                'actvalidationstate_set__previous_state') \
                        .order_by('time'))
                event_ids = [ a.parent_event_id for a in acts if a.parent_event_id ]
                events = EventWithAct.objects.for_today(date) \
                        .filter(patient__service__name=service_name) \
                        .exclude(id__in=event_ids)
                events = [ event.today_occurrence(date) for event in events ]
                acts += [ event.act for event in events if event ]
                for act in acts:
                    if not act.id:
                        act.save()

    logger.write("Traitement des données\n")
    logger.write("----------------------\n\n")
    invoices = {'CMPP' : {}, 'CAMSP' : {}, 'SESSAD TED' : {}, 'SESSAD DYS' : {}}
    for invoice in Invoice.objects.all():
        try:
            patient = PatientRecord.objects.get(id=invoice.patient_id)
            invoices[patient.service.name].setdefault(invoice.invoicing, []).append(invoice)
        except:
            if invoice.patient_id:
                need_mail = True
                logger.write("$$$ La facture %d (%d, %d) a pour id patient %d qui n'existe pas\n" % (invoice.id, invoice.batch, invoice.number, invoice.patient_id))
            else:
                logger.write("La facture %d n'a pas de patient\n" % invoice.id)
            if len(invoice.list_dates.split('$')) > invoice.acts.all().count():
                logger.write("Cette facture présente des actes manquants\n")
    logger.write("Traitement terminé\n\n")

    for service_name in SERVICES:
        service_str = "Service : %s" % service_name
        logger.write('='+'='.join(['' for c in service_str])+"\n")
        logger.write(service_str+"\n")
        logger.write('='+'='.join(['' for c in service_str])+"\n\n")

        acts = Act.objects.filter(date__gte=ANALYSE_SDT.date(), patient__service__name=service_name)

        logger.write("Vérifications Event canceled avec des actes already_billed\n")
        logger.write("---------------------------------------------------------\n\n")
        r_list = []
        for id in set([a.parent_event.id for a in Act.objects.filter(parent_event__canceled = True, already_billed = True)]):
            e = EventWithAct.objects.get(id=id)
            if e.is_recurring():
                logger.write("Recurrent : %d\n" % e.id)
                r_list.append(id)
            elif e.exception_to:
                logger.write("Exception %d au recurrent : %d\n" % (e.id, e.exception_to.id))
                if not e.exception_to.canceled:
                    logger.write("\tLe récurrent n'est pas canceled, we can fix easily setting this exception not canceled\n")
            else:
                logger.write("Simple : %d, we can fix easily setting this exception not canceled\n" % e.id)

        logger.write("\n")

        logger.write("Vérifications des pointages et vérouillages des actes\n")
        logger.write("-----------------------------------------------------\n\n")
        logger.write("*** Les 7 valeurs suivantes doivent rester nulles\n")
        analyse = [[], [], [], [], [], [], [], []]
        for a in acts:
            if not a.last_validation_state:
                analyse[0].append(a)
                need_mail = True
            if a.is_billed and (a.is_new() or a.is_absent()):
                analyse[1].append(a)
                need_mail = True
            if a.validation_locked and a.is_new():
                analyse[2].append(a)
                need_mail = True
            if a.is_billed and not a.validation_locked:
                analyse[3].append(a)
                need_mail = True
            if a.is_state('ACT_LOST'):
                analyse[4].append(a)
                need_mail = True
            if a.is_state('VALIDE') and not a.valide:
                analyse[5].append(a)
                need_mail = True
            if not a.parent_event:
                analyse[6].append(a)
                need_mail = True
            if a.invoice_set.all() and not a.already_billed:
                analyse[7].append(a)
                need_mail = True

        logger.write("$$$ Actes sans valeur 'last validation state' : %d\n" % len(analyse[0]))
        for a in analyse[0]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("$$$ Actes facturés mais non pointés en présent : %d\n" % len(analyse[1]))
        for a in analyse[1]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("$$$ Actes vérouillés mais non pointés : %d\n" % len(analyse[2]))
        for a in analyse[2]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("$$$ Actes facturés mais non vérouillés : %d\n" % len(analyse[3]))
        for a in analyse[3]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("$$$ Actes pointés perdus (déprécié) : %d\n" % len(analyse[4]))
        for a in analyse[4]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("$$$ Actes validés mais avec valeur de contrôle non initialisée : %d\n" % len(analyse[5]))
        for a in analyse[5]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("$$$ Actes sans événement parent : %d\n" % len(analyse[6]))
        for a in analyse[6]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("$$$ Actes deja facturés mais already_billed est False : %d\n" % len(analyse[6]))
        for a in analyse[7]:
            logger.write("\tActe %d : %s\n" % (a.id, a))
        logger.write("\n")


        logger.write("Vérifications des factures\n")
        logger.write("--------------------------\n\n")

        for invoicing, invoice_list in invoices[service_name].items():
            logger.write("Facturation %d\n" % invoicing.seq_id)
            for invoice in invoice_list:
                if len(invoice.list_dates.split('$')) > invoice.acts.all().count():
                    need_mail = True
                    logger.write("$$$ Facture %d (%d, %d) patient %s avec des actes manquants\n" % (invoice.id, invoice.batch or 0, invoice.number or 0, PatientRecord.objects.get(id=invoice.patient_id)))
                    acts_dates = [datetime.strptime(d, '%d/%m/%Y').date() for d in invoice.list_dates.split('$')]
                    if service_name=='CMPP' and len(acts_dates) != len(set(acts_dates)):
                        print "$$$ Il y a plus d'un acte facturé le meme jour!"
                    logger.write("$$$ Nombre d'actes manquants %d\n" % (len(acts_dates)-invoice.acts.all().count()))
                    acts_missing_dates = set(acts_dates) - set([act.date for act in invoice.acts.all()])
                    for date in acts_missing_dates:
                        logger.write("$$$ Il manque un acte le %s\n" % date)
                else:
                    #Chech that dates of acts and dates in list_dates match
                    pass

                for act in invoice.acts.all():
                    if service_name=='CMPP':
                        if not act.is_billed and not act.is_lost:
                            logger.write("Facture %d (%d, %d) patient %s avec acte id %d %s à ce jour en refacturation (normal, autres factures %s)\n" % (invoice.id, invoice.batch or 0, invoice.number or 0, PatientRecord.objects.get(id=invoice.patient_id), act.id, act, str([str(i.number) for i in act.invoice_set.all()])))
                    else:
                        if not act.is_billed:
                            need_mail = True
                            logger.write("$$$ Facture %d (%d, %d) patient %s avec acte id %d %s non is_billed (anormal)\n" % (invoice.id, invoice.batch or 0, invoice.number or 0, PatientRecord.objects.get(id=invoice.patient_id), act.id, act))

        logger.write("\n")

        logger.write("Vérifications des actes facturés\n")
        logger.write("--------------------------------\n\n")


        acts_billed = Act.objects.filter(date__gte=ANALYSE_SDT.date(), patient__service__name=service_name, is_billed=True)
        for act in acts_billed:
            if not act.invoice_set.all():
                logger.write("$$$ Acte facturé sans facture id %d : %s\n" % (act.id, act))
                need_mail = True

        dic = {}
        if service_name=='CMPP':
            for act in acts_billed:
                dic.setdefault(act.patient, []).append(act)
            for patient, acts in dic.items():
                dates = []
                bad_dates = []
                for act in acts:
                    if act.date in dates and not act.date in bad_dates:
                        bad_dates.append(act.date)
                    else:
                        dates.append(act.date)
                for date in bad_dates:
                    need_mail = True
                    logger.write("$$$ %s a des actes facturés le même jour\n" % patient)
                    for act in Act.objects.filter(date=date, patient=patient, is_billed=True):
                        if act.invoice_set.all():
                            logger.write("Acte %d (factures %s) : %s\n" % (act.id, str([i.number for i in act.invoice_set.all()]), act))
                        else:
                            logger.write("Acte %d (sans factures) : %s\n" % (act.id, act))

        logger.write("\n")

        logger.write("Vérifications des jours de validation\n")
        logger.write("-------------------------------------\n\n")


        for date in [(ANALYSE_SDT + timedelta(days=i)).date() for i in range(0, (datetime.today().date()-ANALYSE_SDT.date()).days)]:
            # Actes non pointés
            acts = Act.objects.filter(last_validation_state__state_name='NON_VALIDE', date=date, patient__service__name=service_name)
            if acts:
                for act in acts:
                    if act.validation_locked:
                        need_mail = True
                        logger.write("$$$ Act %d : %s non validé mais verouillé\n" % (act.id, act))
                vms = ValidationMessage.objects.filter(validation_date=date, service__name=service_name)
                if not vms:
                    logger.write("Acte non pointés et aucune opération de validation pour le %s\n" % date)
                else:
                    last = ValidationMessage.objects.filter(validation_date=date, service__name=service_name).latest('when')
                    if last.what != 'Validation automatique':
                        logger.write("Jour %s dévérouillé le %s par %s\n" % (date, last.when, last.who))
                    else:
                        logger.write("$$$ Jour %s vérouillé le %s par %s\n" % (date, last.when, last.who))
                        need_mail = True
                        for act in acts:
                            logger.write("$$$ Act %d : %s\n" % (act.id, act))
                            logger.write("$$$ Evenement parent %d créé par %s le %s\n" % (act.parent_event.id, act.parent_event.creator, act.parent_event.create_date))
                            if act.parent_event.create_date < last.when:
                                logger.write("-------> Création de l'événement antérieur à la validation\n")
                logger.write("\n")

        logger.write("\n")


        logger.write("Vérifications des actes en double\n")
        logger.write("---------------------------------\n\n")

        for date in [(ANALYSE_SDT + timedelta(days=i)).date() for i in range(0, (datetime.today().date()-ANALYSE_SDT.date()).days)]:
            acts = Act.objects.filter(date=date, patient__service__name=service_name).order_by('time')
            if QUIET:
                # En double qu'on ne peut traiter.
                # On en exclue qu'un seul pour voir si un troisième apparait...
                acts = acts.exclude(id__in=(575896, 580500))
            acts_p = {}
            for a in acts:
                acts_p.setdefault(a.patient, []).append(a)
            for p, acts in acts_p.items():
                if len(acts) > 1:
                    acts_t = {}
                    for a in acts:
                        acts_t.setdefault((a.time, a.act_type), []).append(a)
                    for k, aa in acts_t.items():
                        if len(aa) > 1:
                            t, ty = k
                            logger.write("$$$ Actes en double pour %s le %s à %s\n" % (p, date, t))
                            acts_pe = {}
                            for a in aa:
                                acts_pe.setdefault(a.parent_event, []).append(a)
                            if len(aa) == len(acts_pe.keys()):
                                logger.write("$$$ Les événements parents sont distincts\n")
                            else:
                                logger.write("$$$ Il y a des événements parents communs\n")
                            for a in aa:
                                logger.write("\t %d : %s\n" % (a.id, a))
                                logger.write("\t\t %s\n" % a.last_validation_state)
                                if a.is_billed:
                                    logger.write("\t\t Acte facturé\n")
                                if a.invoice_set.all():
                                    logger.write("\t\tHistorique de facturation : %s\n" % str([i.number for i in a.invoice_set.all()]))
                                logger.write("\t\t evenement %d : %s, %s\n" % (a.parent_event.id, a.parent_event.creator, a.parent_event.create_date))
                                if a.parent_event.description:
                                    logger.write("\t\tCommentaire sur event %s\n" % a.parent_event.description.encode('utf-8'))
                                if a.parent_event.canceled:
                                    logger.write("\t\tC'est un événement annulé\n")
                                if a.parent_event.is_recurring():
                                    logger.write("\t\tC'est un événement récurrent\n")
                                if a.parent_event.exception_to:
                                    logger.write("\t\tC'est une exception à %d\n" % a.parent_event.exception_to.id)

        logger.write("\n\n")


    if need_mail or ALWAYS_SEND_MAIL:
        # send_mail
        pass

    logger.write("Fin du script de contôle de Calebasse : %s" % datetime.utcnow())
    old_fn = logger.name
    logger.close()
    os.rename(old_fn, logger_fn)
