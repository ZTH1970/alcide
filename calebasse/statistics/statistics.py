# -*- coding: utf-8 -*-
import os
import tempfile
import csv

from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Count
from django.utils import formats
from django.conf import settings

from calebasse.dossiers.models import PatientRecord, FileState
from calebasse.personnes.models import Worker
from calebasse.actes.models import Act
from calebasse.agenda.models import Event


STATISTICS = {
    'patients_per_worker_for_period' :
        {
        'display_name': 'Enfants suivis par intervenant sur une période',
        'category': 'Patients',
        'comment': """Liste et décompte des patients par intervenant pour les
            patients ayant eu au moins un acte proposé avec cet intervenant
            sur la plage de dates spécifiée. La date de début de la plage par
            défaut est le 1er janvier de l'année en cours. La date de fin de
            la plage par défaut est aujourd'hui. Si aucun patient ou
            intervenant n'est spécifié, tous les patients et les intervenants
            sont pris en compte. A l'inverse, si des patients ou des
            intervenants sont indiqués, seuls ceux-ci sont pris en compte.
            """
    },
    'active_patients_by_state_only' :
        {
        'display_name': "Dossiers actifs selon l'état du dossier à une date donnée",
        'category': 'Patients',
        'comment': """Listes des patients dont le dossier était actif à une date donnée.
            Rappel des états actifs des dossiers : CMPP : diagnostic
            ou traitement, CAMSP : suivi, SESSAD: Traitement.
            La date par défaut est aujourd'hui.
            """
    },
    'active_patients_with_act' :
        {
        'display_name': 'Listes des dossiers avec un acte validé, ou un acte '
            'proposé seulement, sur une période et triés par état du dossier '
            'en fin de période',
        'category': 'Patients',
        'comment': """Listes des dossiers avec un acte validé ou un acte
            proposé seulement sur une période et triés par état du dossier en
            fin de période.
            La date de début de la plage par
            défaut est le 1er janvier de l'année en cours. La date de fin de
            la plage par défaut est aujourd'hui.
            """
    },
    'closed_files' :
        {
        'display_name': 'Dossier clos sur une période et durée de la prise '
            'en charge',
        'category': 'Patients',
        'comment': """Liste des dossiers clos avec leur durée de la prise en
            charge sur la plage de dates spécifiée. Le nombre de dossier et la
            durée moyenne de la prise en charge est également donnée. La date
            de début de la plage par défaut est le 1er janvier de l'année en
            cours. La date de fin de la plage par défaut est aujourd'hui.
            """
    },
    'annual_activity' :
        {
        'display_name': "Activité annuelle",
        'category': 'Intervenants',
        'comment': """Tableaux de synthèse annuelle. La date saisie
            indique l'année à traiter. Si aucune date n'est spécifiée ce sera
            l'année en cours. Si aucun intervenant n'est spécifié, les
            tableaux de synthèse globaux sont retournés. Si des intervenants
            sont indiqués, les tableaux de synthèse pour chaque intervenant
            sont retournés.
            """
    },
    'patients_details' :
        {
        'display_name': "Synthèse par patient",
        'category': 'Patients',
        'comment': """Tableaux de synthèse par patient. Si aucun patient n'est
            indiqué, une synthèse pour chaque patient est retournée. La plage
            de date permet de selectionner les patients pour lesquels au
            moins au acte a été proposé durant cette période. Si un dossier a
            été clos durant cette période mais qu'aucun acte n'a été proposé
            durant cette période, il ne sera pas pris en compte. La date de
            début de la plage par défaut est le 1er janvier de l'année en
            cours. La date de fin de la plage par défaut est aujourd'hui. """
    },
    'patients_synthesis' :
        {
        'display_name': 'Synthèse sur les patients avec un acte valide sur '
            'la plage de date',
        'category': 'Patients',
        'comment': """Patients ayant eu au moins un acte validé
            sur la plage de dates spécifiée. La date de début de la plage par
            défaut est le 1er janvier de l'année en cours. La date de fin de
            la plage par défaut est aujourd'hui.
            """
    },
    'acts_synthesis' :
        {
        'display_name': 'Synthèse sur les actes',
        'category': 'Actes',
        'comment': """Synthèse sur les actes
            sur la plage de dates spécifiée. La date de début de la plage par
            défaut est le 1er janvier de l'année en cours. La date de fin de
            la plage par défaut est aujourd'hui.
            """
    },
    'acts_synthesis_cmpp' :
        {
        'display_name': 'Synthèse sur les dossiers facturés au CMPP',
        'category': 'Patients',
        'services': ['CMPP', ],
        'comment': """Synthèse sur les dossiers facturés au CMPP selon que ce
            soit en diagnostic, en traitement ou les deux,
            sur la plage de dates spécifiée. La date de début de la plage par
            défaut est le 1er janvier de l'année en cours. La date de fin de
            la plage par défaut est aujourd'hui.
            """
    },
    'mises' :
        {
        'display_name': 'Synthèse sur les pathologies MISES',
        'category': 'Patients',
        'comment': """Synthèse sur les pathologies
            sur la plage de dates spécifiée. La date de début de la plage par
            défaut est le 1er janvier de l'année en cours. La date de fin de
            la plage par défaut est aujourd'hui.
            """
    },
    'deficiencies' :
        {
        'display_name': 'Synthèse sur les déficiences',
        'category': 'Patients',
        'comment': """Synthèse sur les déficiences
            sur la plage de dates spécifiée. La date de début de la plage par
            défaut est le 1er janvier de l'année en cours. La date de fin de
            la plage par défaut est aujourd'hui.
            """
    },
    'patients_protection' :
        {
        'display_name': 'Synthèse sur les mesures de protection des patients '
            'à une date donnée',
        'category': 'Patients',
        'comment': """La date par défaut est aujourd'hui.
            """
    },
}

ANNUAL_ACTIVITY_ROWS = ['total', 'pointe', 'non_pointe', 'absent', 'percent_abs', 'reporte', 'acts_present', 'abs_non_exc', 'abs_exc', 'abs_inter', 'annul_nous', 'annul_famille', 'abs_ess_pps', 'enf_hosp', 'non_facturables', 'facturables', 'perdus', 'doubles', 'really_facturables', 'factures', 'diag', 'trait', 'restants_a_fac', 'refac', 'nf', 'percent_nf', 'patients', 'intervenants', 'days', 'fact_per_day', 'moving_time', 'moving_time_per_intervene', 'moving_time_per_act']

ANNUAL_ACTIVITY_COLUMN_LABELS = ['Janv', 'Fév', 'Mar', 'T1', 'Avr', 'Mai', 'Jui', 'T2', 'Jui', 'Aoû', 'Sep', 'T3', 'Oct', 'Nov', 'Déc', 'T4', 'Total']

class AnnualActivityProcessingColumn():
    total = 0
    pointe = 0
    non_pointe = 0
    absent = 0
    percent_abs = 0
    reporte = 0
    acts_present = 0
    abs_non_exc = 0
    abs_exc = 0
    abs_inter = 0
    annul_nous = 0
    annul_famille = 0
    abs_ess_pps = 0
    enf_hosp = 0
    non_facturables = 0
    facturables = 0
    perdus = 0
    doubles = 0
    really_facturables = 0
    factures = 0
    diag = 0
    trait = 0
    restants_a_fac = 0
    refac = 0
    nf = 0
    percent_nf = 0
    patients = 0
    intervenants = 0
    days = 0
    fact_per_day = 0
    moving_time = timedelta()
    moving_time_per_intervene = timedelta()
    moving_time_per_act = timedelta()

def annual_activity_month_analysis(statistic, start_day, analyses, key, i, trim_cnt, participant=None):
    rd = relativedelta(months=1)
    sd = start_day + i * rd
    ed = sd + rd
    acts = None
    moving_events = None
    if participant:
        acts = Act.objects.filter(date__gte=sd.date(),
            date__lt=ed.date(), patient__service=statistic.in_service,
            doctors__in=[participant])
        moving_events = Event.objects.filter(event_type__label='Temps de trajet',
            start_datetime__gte=sd, end_datetime__lt=ed,
            services__in=[statistic.in_service],
            participants__in=[participant])
    else:
        acts = Act.objects.filter(date__gte=sd.date(),
            date__lt=ed.date(), patient__service=statistic.in_service)
        moving_events = Event.objects.filter(event_type__label='Temps de trajet',
            start_datetime__gte=sd, end_datetime__lt=ed,
            services__in=[statistic.in_service])
    analyses[key].append(AnnualActivityProcessingColumn())
    analyses[key][i+trim_cnt].patients = acts.aggregate(Count('patient', distinct=True))['patient__count']
    analyses[key][i+trim_cnt].intervenants = acts.aggregate(Count('doctors', distinct=True))['doctors__count']
    analyses[key][i+trim_cnt].days = acts.aggregate(Count('date', distinct=True))['date__count']
    for me in moving_events:
        analyses[key][i+trim_cnt].moving_time += me.timedelta()
    for a in acts:
        if a.is_new():
            analyses[key][i+trim_cnt].non_pointe += 1
        elif a.is_absent():
            state = a.get_state()
            if state.state_name == 'REPORTE':
                analyses[key][i+trim_cnt].reporte += 1
            else:
                analyses[key][i+trim_cnt].absent += 1
                if state.state_name == 'ABS_NON_EXC':
                    analyses[key][i+trim_cnt].abs_non_exc += 1
                elif state.state_name == 'ABS_EXC':
                    analyses[key][i+trim_cnt].abs_exc += 1
                elif state.state_name == 'ABS_INTER':
                    analyses[key][i+trim_cnt].abs_inter += 1
                elif state.state_name == 'ANNUL_NOUS':
                    analyses[key][i+trim_cnt].annul_nous += 1
                elif state.state_name == 'ANNUL_FAMILLE':
                    analyses[key][i+trim_cnt].annul_famille += 1
                elif state.state_name == 'ABS_ESS_PPS':
                    analyses[key][i+trim_cnt].abs_ess_pps += 1
                elif state.state_name == 'ENF_HOSP':
                    analyses[key][i+trim_cnt].enf_hosp += 1
        else:
            analyses[key][i+trim_cnt].acts_present += 1
            if statistic.in_service.name == 'CMPP':
                if not a.is_billable():
                    analyses[key][i+trim_cnt].non_facturables += 1
                elif a.is_lost:
                    analyses[key][i+trim_cnt].perdus += 1
                elif a.get_state().state_name == 'ACT_DOUBLE':
                    analyses[key][i+trim_cnt].doubles += 1
                elif a.is_billed:
                    analyses[key][i+trim_cnt].factures += 1
                    if a.invoice_set.latest('created').first_tag[0] == 'D':
                        analyses[key][i+trim_cnt].diag += 1
                    else:
                        analyses[key][i+trim_cnt].trait += 1
                else:
                    analyses[key][i+trim_cnt].restants_a_fac += 1
                    if a.invoice_set.all():
                        analyses[key][i+trim_cnt].refac += 1

    analyses[key][i+trim_cnt].total = analyses[key][i+trim_cnt].non_pointe + analyses[key][i+trim_cnt].reporte + analyses[key][i+trim_cnt].absent + analyses[key][i+trim_cnt].acts_present
    analyses[key][i+trim_cnt].pointe = analyses[key][i+trim_cnt].total - analyses[key][i+trim_cnt].non_pointe
    percent_abs = 100
    if not analyses[key][i+trim_cnt].pointe or not analyses[key][i+trim_cnt].absent:
        percent_abs = 0
    elif analyses[key][i+trim_cnt].absent:
        percent_abs = (analyses[key][i+trim_cnt].absent/float(analyses[key][i+trim_cnt].pointe))*100
    analyses[key][i+trim_cnt].percent_abs = "%.2f" % percent_abs

    if statistic.in_service.name == 'CMPP':
        analyses[key][i+trim_cnt].facturables = analyses[key][i+trim_cnt].acts_present - analyses[key][i+trim_cnt].non_facturables
        analyses[key][i+trim_cnt].really_facturables = analyses[key][i+trim_cnt].facturables - analyses[key][i+trim_cnt].perdus - analyses[key][i+trim_cnt].doubles
        analyses[key][i+trim_cnt].nf = analyses[key][i+trim_cnt].perdus + analyses[key][i+trim_cnt].doubles + analyses[key][i+trim_cnt].non_facturables # + analyses[key][i+trim_cnt].reporte
        percent_nf = 100
        if not analyses[key][i+trim_cnt].pointe or not analyses[key][i+trim_cnt].nf:
            percent_nf = 0
        elif analyses[key][i+trim_cnt].nf:
            percent_nf = (analyses[key][i+trim_cnt].nf/float(analyses[key][i+trim_cnt].pointe))*100
        analyses[key][i+trim_cnt].percent_nf = "%.2f" % percent_nf
        if analyses[key][i+trim_cnt].days:
            analyses[key][i+trim_cnt].fact_per_day = "%.2f" % (analyses[key][i+trim_cnt].really_facturables / float(analyses[key][i+trim_cnt].days))

    if analyses[key][i+trim_cnt].moving_time and analyses[key][i+trim_cnt].intervenants:
        analyses[key][i+trim_cnt].moving_time_per_intervene = analyses[key][i+trim_cnt].moving_time / analyses[key][i+trim_cnt].intervenants
    if analyses[key][i+trim_cnt].moving_time and analyses[key][i+trim_cnt].acts_present:
        analyses[key][i+trim_cnt].moving_time_per_act = analyses[key][i+trim_cnt].moving_time / analyses[key][i+trim_cnt].acts_present


def annual_activity_trimester_analysis(statistic, start_day, analyses, key, i, trim_cnt, participant=None):
    analyses[key].append(AnnualActivityProcessingColumn())
    rd = relativedelta(months=1)
    sd = start_day + i * rd
    start = start_day + (i-2) * rd
    end = sd + rd
    acts = None
    if participant:
        acts = Act.objects.filter(date__gte=start.date(),
            date__lt=end.date(), patient__service=statistic.in_service,
            doctors__in=[participant])
    else:
        acts = Act.objects.filter(date__gte=start.date(),
            date__lt=end.date(), patient__service=statistic.in_service)
    for row in ANNUAL_ACTIVITY_ROWS:
        if row == 'percent_abs':
            pointe = analyses[key][i+trim_cnt-1].pointe + analyses[key][i-2+trim_cnt].pointe + analyses[key][i-3+trim_cnt].pointe
            tot_abs = analyses[key][i+trim_cnt-1].absent + analyses[key][i-2+trim_cnt].absent + analyses[key][i-3+trim_cnt].absent
            percent_abs = 100
            if not pointe or not tot_abs:
                percent_abs = 0
            elif tot_abs:
                percent_abs = (tot_abs/float(pointe))*100
            analyses[key][i+trim_cnt].percent_abs = "%.2f" % percent_abs
        elif row == 'percent_nf':
            pointe = analyses[key][i+trim_cnt-1].pointe + analyses[key][i-2+trim_cnt].pointe + analyses[key][i-3+trim_cnt].pointe
            tot_nf = analyses[key][i+trim_cnt-1].nf + analyses[key][i-2+trim_cnt].nf + analyses[key][i-3+trim_cnt].nf
            percent_nf = 100
            if not pointe or not tot_nf:
                percent_nf = 0
            elif tot_nf:
                percent_nf = (tot_nf/float(pointe))*100
            analyses[key][i+trim_cnt].percent_nf = "%.2f" % percent_nf
        elif row == 'patients':
            analyses[key][i+trim_cnt].patients = acts.aggregate(Count('patient', distinct=True))['patient__count']
        elif row == 'intervenants':
            analyses[key][i+trim_cnt].intervenants = acts.aggregate(Count('doctors', distinct=True))['doctors__count']
        elif row == 'fact_per_day':
            if analyses[key][i+trim_cnt].days:
                analyses[key][i+trim_cnt].fact_per_day = "%.2f" % (analyses[key][i+trim_cnt].really_facturables / float(analyses[key][i+trim_cnt].days))
        elif row == 'moving_time_per_intervene':
            if analyses[key][i+trim_cnt].moving_time and analyses[key][i+trim_cnt].intervenants:
                analyses[key][i+trim_cnt].moving_time_per_intervene = analyses[key][i+trim_cnt].moving_time / analyses[key][i+trim_cnt].intervenants
        elif row == 'moving_time_per_act':
            if analyses[key][i+trim_cnt].moving_time and analyses[key][i+trim_cnt].acts_present:
                analyses[key][i+trim_cnt].moving_time_per_act = analyses[key][i+trim_cnt].moving_time / analyses[key][i+trim_cnt].acts_present
        else:
            setattr(analyses[key][i+trim_cnt], row, getattr(analyses[key][i+trim_cnt-1], row) + getattr(analyses[key][i-2+trim_cnt], row) + getattr(analyses[key][i-3+trim_cnt], row))

def annual_activity_synthesis_analysis(statistic, start_day, end_day, analyses, key, participant=None):
    analyses[key].append(AnnualActivityProcessingColumn())
    acts = None
    if participant:
        acts = Act.objects.filter(date__gte=start_day.date(),
            date__lt=end_day.date(), patient__service=statistic.in_service,
            doctors__in=[participant])
    else:
        acts = Act.objects.filter(date__gte=start_day.date(),
            date__lt=end_day.date(), patient__service=statistic.in_service)
    for row in ANNUAL_ACTIVITY_ROWS:
        if row == 'percent_abs':
            tot_abs = 0
            pointe = 0
            for i in (3, 7, 11, 15):
                pointe += analyses[key][i].pointe
                tot_abs += analyses[key][i].absent
            percent_abs = 100
            if not pointe or not tot_abs:
                percent_abs = 0
            elif tot_abs:
                percent_abs = (tot_abs/float(pointe))*100
            analyses[key][16].percent_abs = "%.2f" % percent_abs
        elif row == 'percent_nf':
            tot_nf= 0
            pointe = 0
            for i in (3, 7, 11, 15):
                pointe += analyses[key][i].pointe
                tot_nf += analyses[key][i].nf
            percent_nf = 100
            if not pointe or not tot_nf:
                percent_nf = 0
            elif tot_nf:
                percent_nf = (tot_nf/float(pointe))*100
            analyses[key][16].percent_nf = "%.2f" % percent_nf
        elif row == 'patients':
            analyses[key][16].patients = acts.aggregate(Count('patient', distinct=True))['patient__count']
        elif row == 'intervenants':
            analyses[key][16].intervenants = acts.aggregate(Count('doctors', distinct=True))['doctors__count']
        elif row == 'fact_per_day':
            if analyses[key][16].days:
                analyses[key][16].fact_per_day = "%.2f" % (analyses[key][16].really_facturables / float(analyses[key][16].days))
        elif row == 'moving_time_per_intervene':
            if analyses[key][16].moving_time and analyses[key][16].intervenants:
                analyses[key][16].moving_time_per_intervene = analyses[key][16].moving_time / analyses[key][16].intervenants
        elif row == 'moving_time_per_act':
            if analyses[key][16].moving_time and analyses[key][16].acts_present:
                analyses[key][16].moving_time_per_act = analyses[key][16].moving_time / analyses[key][16].acts_present
        else:
            val = 0
            if row == 'moving_time':
                val = timedelta()
            for i in (3, 7, 11, 15):
                val += getattr(analyses[key][i], row)
            setattr(analyses[key][16], row, val)

def strfdelta(tdelta, fmt):
    if not tdelta:
        return '0'
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

def annual_activity_build_tables(statistic, analyses, key, label, data_tables):
    table_1 = []
    table_1_label = label + ' - général'
    table_1.append([table_1_label] + ANNUAL_ACTIVITY_COLUMN_LABELS)
    rows = []
    row = ['Proposés']
    for column in analyses[key]:
        row.append(column.total)
    rows.append(row)
    row = ['Non pointés']
    for column in analyses[key]:
        row.append(column.non_pointe)
    rows.append(row)
    row = ['Absences']
    for column in analyses[key]:
        row.append(column.absent)
    rows.append(row)
    row = ['Reportés']
    for column in analyses[key]:
        row.append(column.reporte)
    rows.append(row)
    row = ['Présents']
    for column in analyses[key]:
        row.append(column.acts_present)
    rows.append(row)
    if statistic.in_service.name == 'CMPP':
        row = ['Facturables']
        for column in analyses[key]:
            row.append(column.really_facturables)
        rows.append(row)
        row = ['Facturés']
        for column in analyses[key]:
            row.append(column.factures)
        rows.append(row)
        row = ['Diagnostics']
        for column in analyses[key]:
            row.append(column.diag)
        rows.append(row)
        row = ['Traitements']
        for column in analyses[key]:
            row.append(column.trait)
        rows.append(row)
        row = ['Restants à facturer']
        for column in analyses[key]:
            row.append(column.restants_a_fac)
        rows.append(row)
        row = ['Dont en refact.']
        for column in analyses[key]:
            row.append(column.refac)
        rows.append(row)
    row = ['Patients']
    for column in analyses[key]:
        row.append(column.patients)
    rows.append(row)
    row = ['Intervenants']
    for column in analyses[key]:
        row.append(column.intervenants)
    rows.append(row)
    row = ['Jours']
    for column in analyses[key]:
        row.append(column.days)
    rows.append(row)
    if statistic.in_service.name == 'CMPP':
        row = ['Facturables / jour']
        for column in analyses[key]:
            row.append(column.fact_per_day)
        rows.append(row)
    row = ['Temps de déplacement']
    for column in analyses[key]:
        row.append(strfdelta(column.moving_time, "{hours}h {minutes}m"))
        if column.moving_time.days:
            row.append(strfdelta(column.moving_time, "{days}j {hours}h {minutes}m"))
    rows.append(row)
    row = ['Temps de déplacement par intervenant']
    for column in analyses[key]:
        row.append(strfdelta(column.moving_time_per_intervene, "{hours}h {minutes}m"))
        if column.moving_time_per_intervene.days:
            row.append(strfdelta(column.moving_time_per_intervene, "{days}j {hours}h {minutes}m"))
    rows.append(row)
    row = ['Temps de déplacement par acte']
    for column in analyses[key]:
        row.append(strfdelta(column.moving_time_per_act, "{hours}h {minutes}m"))
        if column.moving_time_per_act.days:
            row.append(strfdelta(column.moving_time_per_act, "{days}j {hours}h {minutes}m"))
    rows.append(row)
    table_1.append(rows)
    data_tables.append(table_1)

    table_2 = []
    table_2_label = label + ' - absences'
    table_2.append([table_2_label] + ANNUAL_ACTIVITY_COLUMN_LABELS)
    rows = []
    row = ['Pointés']
    for column in analyses[key]:
        row.append(column.pointe)
    rows.append(row)
    row = ['Absences']
    for column in analyses[key]:
        row.append(column.absent)
    rows.append(row)
    row = ['% absences / pointés']
    for column in analyses[key]:
        row.append(column.percent_abs)
    rows.append(row)
    row = ['Excusées']
    for column in analyses[key]:
        row.append(column.abs_exc)
    rows.append(row)
    row = ['Non excusées']
    for column in analyses[key]:
        row.append(column.abs_non_exc)
    rows.append(row)
    row = ["De l'intervenant"]
    for column in analyses[key]:
        row.append(column.abs_inter)
    rows.append(row)
    row = ["Annulés par nous"]
    for column in analyses[key]:
        row.append(column.annul_nous)
    rows.append(row)
    row = ['Annulés par la famille']
    for column in analyses[key]:
        row.append(column.annul_famille)
    rows.append(row)
    row = ['ESS PPS']
    for column in analyses[key]:
        row.append(column.abs_ess_pps)
    rows.append(row)
    row = ['Hospitalisations']
    for column in analyses[key]:
        row.append(column.enf_hosp)
    rows.append(row)
    table_2.append(rows)
    data_tables.append(table_2)

    if statistic.in_service.name == 'CMPP':
        table_3 = []
        table_3_label = label + ' - non fact.'
        table_3.append([table_3_label] + ANNUAL_ACTIVITY_COLUMN_LABELS)
        rows = []
        row = ['Pointés']
        for column in analyses[key]:
            row.append(column.pointe)
        rows.append(row)
        row = ['Présents']
        for column in analyses[key]:
            row.append(column.acts_present)
        rows.append(row)
        row = ['De type non fact.']
        for column in analyses[key]:
            row.append(column.non_facturables)
        rows.append(row)
        row = ['De type fact.']
        for column in analyses[key]:
            row.append(column.facturables)
        rows.append(row)
        row = ['Perdus']
        for column in analyses[key]:
            row.append(column.perdus)
        rows.append(row)
        row = ['En doubles']
        for column in analyses[key]:
            row.append(column.doubles)
        rows.append(row)
        row = ['Non facturables']
        for column in analyses[key]:
            row.append(column.nf)
        rows.append(row)
        row = ['% NF / pointés']
        for column in analyses[key]:
            row.append(column.percent_nf)
        rows.append(row)
        table_3.append(rows)
        data_tables.append(table_3)

def run_annual_activity(statistic, start_day, analyses, key, label, data_tables, participant=None):
    analyses[key] = list()
    trim_cnt = 0
    for i in range(0, 12):
        annual_activity_month_analysis(statistic, start_day, analyses, key, i, trim_cnt, participant)
        if not (i + 1) % 3:
            trim_cnt += 1
            annual_activity_trimester_analysis(statistic, start_day, analyses, key, i, trim_cnt, participant)
    end_day = datetime(start_day.year+1, 1, 1)
    annual_activity_synthesis_analysis(statistic, start_day, end_day, analyses, key, participant)
    annual_activity_build_tables(statistic, analyses, key, label, data_tables)

def annual_activity(statistic):
    if not statistic.in_service:
        return None
    start_day = datetime(datetime.today().year, 1, 1)
    if statistic.in_year:
        start_day = datetime(statistic.in_year, 1, 1)
    data_tables = list()
    analyses = dict()
    if not statistic.in_participants:
        run_annual_activity(statistic, start_day, analyses, 'global', str(statistic.in_year) + ' - Tous', data_tables, participant=None)
    else:
        for participant in statistic.in_participants:
            run_annual_activity(statistic, start_day, analyses, participant.id, str(statistic.in_year) + ' - ' + str(participant), data_tables, participant=participant)
    return [data_tables]

def patients_per_worker_for_period(statistic):
    if not statistic.in_service:
        return None
    data_tables = []
    data = []
    data.append(['Intervenants', 'Nombre', 'Patients'])
    values = []
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    acts = None
    if statistic.in_patients:
        acts = Act.objects.filter(date__gte=statistic.in_start_date,
            date__lte=statistic.in_end_date,
            patient__service=statistic.in_service,
            patient__in=statistic.in_patients)
    else:
        acts = Act.objects.filter(date__gte=statistic.in_start_date,
            date__lte=statistic.in_end_date,
            patient__service=statistic.in_service)
    analyse = dict()
    for act in acts:
        for intervene in act.doctors.all():
            if statistic.in_participants:
                if intervene in statistic.in_participants:
                    analyse.setdefault(intervene, []).append(str(act.patient))
            else:
                analyse.setdefault(intervene, []).append(str(act.patient))
    o_analyse = OrderedDict(sorted(analyse.items(), key=lambda t: t[0]))
    for intervene, patients in o_analyse.iteritems():
        lst = list(set(patients))
        values.append([str(intervene), len(lst), lst])
    data.append(values)
    data_tables.append(data)
    return [data_tables]

def active_patients_by_state_only(statistic):
    if not statistic.in_service:
        return None
    if not statistic.in_start_date:
        statistic.in_start_date = datetime.today()
    active_states = None
    if statistic.in_service.name == 'CMPP':
        active_states = ('TRAITEMENT', 'DIAGNOSTIC')
    elif statistic.in_service.name == 'CAMSP':
        active_states = ('SUIVI', )
    else:
        active_states = ('TRAITEMENT', )
    patients = [(p.last_name, p.first_name, p.paper_id) \
        for p in PatientRecord.objects.filter(service=statistic.in_service) \
            if p.get_state_at_day(
                statistic.in_start_date).status.type in active_states]
    data_tables_set=[[[['En date du :', formats.date_format(statistic.in_start_date, "SHORT_DATE_FORMAT"), len(patients)]]]]
    data = []
    data.append(['Nom', 'Prénom', 'N° Dossier'])
    p_list = []
    for ln, fn, pid in patients:
        ln = ln or ''
        if len(ln) > 1:
            ln = ln[0].upper() + ln[1:].lower()
        fn = fn or ''
        if len(fn) > 1:
            fn = fn[0].upper() + fn[1:].lower()
        p_list.append((ln, fn, str(pid or '')))
    data.append(sorted(p_list,
        key=lambda k: k[0]+k[1]))
    data_tables_set[0].append(data)
    return data_tables_set

def patients_protection(statistic):
    if not statistic.in_service:
        return None
    if not statistic.in_start_date:
        statistic.in_start_date = datetime.today()
    patients = PatientRecord.objects.filter(protectionstate__isnull=False).distinct()
    protection_states = [p.get_protection_state_at_date(
            statistic.in_start_date) for p in patients
            if p.get_protection_state_at_date(statistic.in_start_date)]
    analyse = {}
    for state in protection_states:
        analyse.setdefault(state.status.name, 0)
        analyse[state.status.name] += 1
    data_tables_set=[[[['En date du :', formats.date_format(statistic.in_start_date, "SHORT_DATE_FORMAT"), len(protection_states)]]]]
    data = []
    data.append(['Mesure de protection', 'Nombre de dossiers'])
    data.append(analyse.items())
    data_tables_set[0].append(data)
    return data_tables_set

def active_patients_with_act(statistic):
    def process(patients_list, title):
        data_tables = []
        data = []
        data.append([title, len(patients_list), '', ''])
        data_tables.append(data)
        data = []
        data.append(['Nom', 'Prénom', 'N° Dossier'])
        p_list = []
        for p in patients_list:
            ln, fn, pid = p.last_name, p.first_name, p.paper_id
            ln = ln or ''
            if len(ln) > 1:
                ln = ln[0].upper() + ln[1:].lower()
            fn = fn or ''
            if len(fn) > 1:
                fn = fn[0].upper() + fn[1:].lower()
            p_list.append((ln, fn, str(pid or '')))
        data.append(sorted(p_list,
            key=lambda k: k[0]+k[1]))
        data_tables.append(data)
        return data_tables
    if not statistic.in_service:
        return None
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    active_states = None
    if statistic.in_service.name == 'CMPP':
        active_states = ('TRAITEMENT', 'DIAGNOSTIC')
    elif statistic.in_service.name == 'CAMSP':
        active_states = ('SUIVI', )
    else:
        active_states = ('TRAITEMENT', )

    data_tables_set = []
    data_tables = []
    data = []
    data.append(['Période', 'Jours'])
    data.append([("%s - %s"
        % (formats.date_format(statistic.in_start_date, "SHORT_DATE_FORMAT"),
        formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT")),
        (statistic.in_end_date-statistic.in_start_date).days+1)])
    data_tables.append(data)
    data_tables_set.append(data_tables)

    acts_base = Act.objects.filter(
        date__gte=statistic.in_start_date,
        date__lte=statistic.in_end_date,
        patient__service=statistic.in_service)
    acts_valide = acts_base.filter(valide=True)
    acts_valide_patients_ids = acts_valide.order_by('patient').\
        distinct('patient').values_list('patient')
    acts_valide_patients = PatientRecord.objects.filter(
        id__in=[patient[0] for patient in acts_valide_patients_ids])
    all_patients_ids = acts_base.order_by('patient').distinct('patient').\
        values_list('patient')
    acts_not_valide_patients = PatientRecord.objects.filter(
        id__in=[patient[0] for patient in all_patients_ids
            if not patient in acts_valide_patients_ids])

    data_tables_set.append(process(acts_valide_patients, "Patients avec un acte validé sur la période"))
    p_val = dict()
    for p in acts_valide_patients:
        p_val.setdefault(p.get_state_at_day(statistic.in_end_date).status, []).append(p)
    for k, v in p_val.items():
        data_tables_set.append(process(v, "Patients avec un acte validé et dans l'état '%s' en date du %s" % (k, formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT"))))
    p_val = dict()
    data_tables_set.append(process(acts_not_valide_patients, "Patients avec un acte proposé seulement sur la période"))
    for p in acts_not_valide_patients:
        p_val.setdefault(p.get_state_at_day(statistic.in_end_date).status, []).append(p)
    for k, v in p_val.items():
        data_tables_set.append(process(v, "Patients avec sans acte validé et dans l'état '%s' en date du %s" % (k, formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT"))))

    return data_tables_set

def closed_files(statistic):
    if not statistic.in_service:
        return None
    data_tables = []
    data1 = []
    data1.append(['Période', 'Jours',
        'Nombre de dossiers clos durant la période', 'PEC totale', 'PEC moyenne', "Dossiers qui ne sont plus clos"])
    data2 = []
    data2.append(['Nom', 'Prénom', 'N° Dossier', 'Date de clôture', 'Durée de la PEC', "N'est plus clos"])
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    closed_records = FileState.objects.filter(status__type='CLOS',
        date_selected__gte=statistic.in_start_date,
        date_selected__lte=statistic.in_end_date). \
        order_by('patient').distinct('patient').\
        values_list('patient')
    closed_records = PatientRecord.objects.filter(service=statistic.in_service, id__in=[patient[0]
        for patient in closed_records])
    total_pec = 0
    p_list = []
    not_closed_now = 0
    for record in closed_records:
        ln = record.last_name or ''
        if len(ln) > 1:
            ln = ln[0].upper() + ln[1:].lower()
        fn = record.first_name or ''
        if len(fn) > 1:
            fn = fn[0].upper() + fn[1:].lower()
        current_state = ''
        close_date = record.last_state.date_selected.date()
        if record.get_current_state().status.type != 'CLOS':
            not_closed_now += 1
            current_state = record.get_current_state().status.name + \
                ' le ' + formats.date_format(record.get_current_state(). \
                date_selected, "SHORT_DATE_FORMAT")
            close_date = FileState.objects.filter(status__type='CLOS',
                patient=record).order_by('-date_selected')[0].date_selected.date()
        p_list.append((ln, fn, str(record.paper_id or ''),
            close_date,
            record.care_duration_since_last_contact_or_first_act,
            current_state))
        total_pec += record.care_duration_since_last_contact_or_first_act
    data2.append(sorted(p_list,
        key=lambda k: k[0]+k[1]))
    avg_pec = 0
    if closed_records.count() and total_pec:
        avg_pec = total_pec/closed_records.count()
    data1.append([("%s - %s"
        % (formats.date_format(statistic.in_start_date, "SHORT_DATE_FORMAT"),
        formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT")),
        (statistic.in_end_date-statistic.in_start_date).days+1,
        closed_records.count(), total_pec, avg_pec, not_closed_now)])
    data_tables.append(data1)
    data_tables.append(data2)

    days_states = {}
    for record in closed_records:
        for state, duration in record.get_states_history_with_duration():
            days_states.setdefault(state.status, 0)
            days_states[state.status] += duration.days
    data = []
    data.append(["Etat des dossiers", "Nombre de jours total", "Nombre de jours moyen par dossier"])
    values = []
    for status, duration in days_states.iteritems():
        values.append((status.name, duration, duration/closed_records.count()))
    data.append(values)
    data_tables.append(data)
    return [data_tables]

def patients_details(statistic):
    if not statistic.in_service:
        return None
    data_tables_set = []
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    acts = None
    if statistic.in_patients:
        acts = Act.objects.filter(date__gte=statistic.in_start_date,
            date__lte=statistic.in_end_date,
            patient__service=statistic.in_service,
            patient__in=statistic.in_patients)
    else:
        acts = Act.objects.filter(date__gte=statistic.in_start_date,
            date__lte=statistic.in_end_date,
            patient__service=statistic.in_service)
    analyse = dict()
    for act in acts:
        analyse.setdefault(act.patient, []).append(act)
    o_analyse = OrderedDict(sorted(analyse.items(),
        key=lambda t: t[0].last_name))
    data = []
    data.append(['Période', 'Jours',
        'Nombre de dossiers'])
    data.append([("%s - %s"
        % (formats.date_format(statistic.in_start_date, "SHORT_DATE_FORMAT"),
        formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT")),
        (statistic.in_end_date-statistic.in_start_date).days+1,
        len(o_analyse))])
    data_tables_set.append([data])
    for patient, acts in o_analyse.iteritems():
        data_tables = list()
        data_tables.append([["%s %s" % (str(patient), str(patient.paper_id))]])
        data_tables.append([["Durée de la prise en charge (depuis le premier acte)"], [[patient.care_duration_since_last_contact_or_first_act]]])
        data = []
        data.append(["Statut de l'acte", 'Nombre'])
        values = []
        values.append(('Proposés', len(acts)))
        np, absent = 0, 0
        act_types = dict()
        for a in acts:
            if a.is_new():
                np += 1
            elif a.is_absent():
                absent += 1
            act_types.setdefault(a.act_type, []).append(a)
        values.append(('Non pointés', np))
        values.append(('Présents', len(acts) - np - absent))
        values.append(('Absents', absent))
        data.append(values)
        data_tables.append(data)

        data = []
        data.append(["Types d'acte", "Nombre d'actes proposés", "Nombre d'actes réalisés"])
        values = []
        for act_type, acts in act_types.iteritems():
            values.append((act_type, len(acts), len([a for a in acts if a.is_present()])))
        data.append(values)
        data_tables.append(data)

        data = []
        data.append(["Historique", "Nombre de jours par état"])
        values = []
        for state, duration in patient.get_states_history_with_duration():
            values.append(("%s (%s)" % (state.status.name,
                formats.date_format(state.date_selected,
                "SHORT_DATE_FORMAT")), duration.days))
        data.append(values)
        data_tables.append(data)

        contacts = FileState.objects.filter(patient=patient, status__type='ACCUEIL').order_by('date_selected')
        recontact = 'Non'
        last_contact = None
        first_acts_after_contact = None
        if len(contacts) == 1:
            last_contact = contacts[0]
        elif len(contacts) > 1:
            recontact = 'Oui'
            last_contact = contacts[len(contacts)-1]
        if last_contact:
            # inscription act
            first_acts_after_contact = Act.objects.filter(patient=patient, date__gte=last_contact.date_selected).order_by('date')
            if first_acts_after_contact:
                first_act_after_contact = first_acts_after_contact[0]
                if first_act_after_contact.date <= statistic.in_end_date.date() and first_act_after_contact.date >= statistic.in_start_date.date():
                    # inscription during the selected date range.
                    waiting_duration = first_act_after_contact.date - last_contact.date_selected.date()
                    data = []
                    data.append(["Date inscription", "Date accueil", 'Attente', 'Réinscription'])
                    values = []
                    values.append((first_act_after_contact.date, last_contact.date_selected.date(), waiting_duration.days, recontact))
                    data.append(values)
                    data_tables.append(data)

        closed_during_range_date = None
        try:
            closed_during_range_date = FileState.objects.filter(patient=patient, status__type='CLOS',
                date_selected__gte=statistic.in_start_date,
                date_selected__lte=statistic.in_end_date).latest('date_selected')
        except:
            pass
        care_duration = patient.care_duration_since_last_contact_or_first_act
        closure_date = ''
        if closed_during_range_date:
            closure_date = closed_during_range_date.date_selected.date
        reopen = ''
        if closed_during_range_date and not patient.exit_date:
            reopen = 'Oui'
        data = []
        data.append(["Durée de la prise en charge", "Clos pendant la période", "Actes suivants la clôture"])
        values = []
        values.append((patient.care_duration_since_last_contact_or_first_act, closure_date, reopen))
        data.append(values)
        data_tables.append(data)

        if patient.mdph_requests.exists():
            data = []
            data.append(["Demande(s) MDPH pendant la période", "Date de la demande", "Demande antérieure à la date de début saisie"])
            values = []
            for request in patient.mdph_requests.order_by('start_date'):
                before = 'Non'
                if request.start_date < statistic.in_start_date.date():
                    before = 'Oui'
                values.append(('MDPH : ' + request.mdph.department, request.start_date, before))
            data.append(values)
            data_tables.append(data)
        if patient.mdph_responses.exists():
            data = []
            data.append(["Réponse(s) MDPH pendant la période", "Date de début", "Date de fin"])
            values = []
            for response in patient.mdph_responses.order_by('start_date'):
                values.append(('MDPH : ' + response.mdph.department, response.start_date, response.end_date))
            data.append(values)
            data_tables.append(data)
        data_tables_set.append(data_tables)

    return data_tables_set

def patients_synthesis(statistic):
    if not statistic.in_service:
        return None
    data_tables = []
    data = []
    data.append(['Période', 'Jours',
        'Nombre de dossiers avec un acte validé sur la période',
        "Nombre d'actes validés sur la période"])
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    acts = Act.objects.filter(valide=True,
        date__gte=statistic.in_start_date,
        date__lte=statistic.in_end_date,
        patient__service=statistic.in_service)
    patients = acts.order_by('patient').distinct('patient').\
        values_list('patient')
    patients = PatientRecord.objects.filter(id__in=[patient[0]
        for patient in patients])

    active_states = None
    if statistic.in_service.name == 'CMPP':
        active_states = ('TRAITEMENT', 'DIAGNOSTIC', )
    elif statistic.in_service.name == 'CAMSP':
        active_states = ('SUIVI', 'BILAN', 'SURVEILLANCE', 'CLOS', )
    else:
        active_states = ('TRAITEMENT', )

    inscriptions = []
    for patient in patients:
        # Select patient if she has been in treament between the selected dates
        traitement_states_tmp = FileState.objects.filter(patient=patient, status__type__in=active_states, date_selected__lte=statistic.in_end_date).order_by('date_selected')
        traitement_states = []
        for ts in traitement_states_tmp:
            if not ts.get_next_state() or ts.get_next_state().date_selected >= statistic.in_start_date:
                traitement_states.append(ts)

        # Patient has been in treatment
        # We look for all the treament periods during the selected dates
        # A treament period ends if during the period the file has left treament state
        openings = []
        opening = []
        start = False
        for ts in traitement_states:
            if start:
                openings.append(opening)
                opening = []
                start = False
            if ts.get_next_state() and not ts.get_next_state().status.type in active_states and ts.get_next_state().get_next_state() and ts.get_next_state().get_next_state().status.type in active_states:
                start = True
            opening.append(ts)
        openings.append(opening)

        # The first treatment state is the first one of each period matching the dates selected.
        # But there could be other treatment state before, like diag before treatment.
        # so We have to look for the very first treament state to look at the first act after
        first_tss = []
        for opening in openings:
            if len(opening) >= 1:
                first_ts = opening[0]
                while first_ts.previous_state and first_ts.previous_state.status.type in active_states:
                    first_ts = first_ts.previous_state
                contact = None
                if first_ts.previous_state and first_ts.previous_state.status.type=='ACCUEIL':
                    contact = first_ts.previous_state.date_selected.date()
                first_tss.append((contact, first_ts))

        # We look to the first act after the datebeginning
        for contact, first_ts in first_tss:
            acts_tmp = Act.objects.filter(valide=True,
                date__gte=first_ts.date_selected,
                patient=patient).order_by('date')
            if acts_tmp and acts_tmp[0].date >= statistic.in_start_date.date() and acts_tmp[0].date <= statistic.in_end_date.date():
                waiting_duration = 0
                if contact:
                    waiting_duration = (acts_tmp[0].date - contact).days
                inscriptions.append((patient, contact, first_ts.date_selected.date(), acts_tmp[0].date, waiting_duration))

    if statistic.inscriptions:
        patients = PatientRecord.objects.filter(id__in=[p.id for p, _, _, _, _ in inscriptions])
        acts = acts.filter(patient__in=patients)

    nb_patients = patients.count()
    if not nb_patients:
        return []

    data.append([("%s - %s"
        % (formats.date_format(statistic.in_start_date, "SHORT_DATE_FORMAT"),
        formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT")),
        (statistic.in_end_date-statistic.in_start_date).days+1,
        nb_patients, acts.count())])
    data_tables.append(data)
    data = []
    data.append(['Féminin', 'Masculin'])
    data.append([(patients.filter(gender='2').count(),
        patients.filter(gender='1').count())])
    data_tables.append(data)
    data = []
    data.append(['Durée totale de la PEC',
        'Durée moyenne de la PEC par patient'])
    pec_total = sum([p.care_duration_since_last_contact_or_first_act for p in patients])
    data.append([(pec_total, pec_total/nb_patients)])
    data_tables.append(data)

    data = []
    data.append(["Etat du dossier à ce jour (%s)" % formats.date_format(datetime.today(), "SHORT_DATE_FORMAT"), 'Nombre de patients'])
    states = dict()
    for patient in patients:
        states.setdefault(patient.get_current_state().status, []).append(patient)
    values = []
    for state, ps in states.iteritems():
        values.append((state.name, len(ps)))
    data.append(values)
    data_tables.append(data)

    data = []
    data.append(["Etat du dossier en date de fin (%s)" % formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT"), 'Nombre de patients'])
    states = dict()
    for patient in patients:
        states.setdefault(patient.get_state_at_day(statistic.in_end_date).status, []).append(patient)
    values = []
    for state, ps in states.iteritems():
        values.append((state.name, len(ps)))
    data.append(values)
    data_tables.append(data)

    data = []
    data.append(["Inscriptions (premier acte suivant le début d'une phase de traitement dans la période)", "Durée moyenne de l'attente"])
    data.append([(len(inscriptions), sum([wd for _, _, _, _, wd in inscriptions])/len(inscriptions) if len(inscriptions) else 0)])
    data_tables.append(data)

    if inscriptions:
        data = []
        data.append(['Nom', 'Prénom', "Numéro papier", "Date premier acte", "Date passage en traitement", "Date de contact", "Attente"])
        values = []
        for patient, contact, first_ts, first_act, waiting_duration in sorted(inscriptions, key=lambda p: (p[0].last_name, p[0].first_name)):
            values.append((patient.last_name, patient.first_name, patient.paper_id, first_act, first_ts, contact, waiting_duration))
        data.append(values)
        data_tables.append(data)

    closed_records = FileState.objects.filter(status__type='CLOS',
        date_selected__gte=statistic.in_start_date,
        date_selected__lte=statistic.in_end_date, patient__in=patients). \
        order_by('patient').distinct('patient').\
        values_list('patient')
    closed_records = PatientRecord.objects.filter(service=statistic.in_service, id__in=[patient[0]
        for patient in closed_records])
    total_pec = 0
    not_closed_now = 0
    for record in closed_records:
        if record.get_current_state().status.type != 'CLOS':
            not_closed_now += 1
        total_pec += record.care_duration_since_last_contact_or_first_act
    avg_pec = 0
    if closed_records.count() and total_pec:
        avg_pec = total_pec/closed_records.count()
    if closed_records.count():
        data = []
        data.append(['Clos dans la période', 'Durée totale de la PEC', 'Durée moyenne de la PEC', "Qui ne sont plus clos à ce jour"])
        data.append([(closed_records.count(), total_pec, avg_pec, not_closed_now)])
        data_tables.append(data)

    mdph_requests = 0
    mdph_requests_before = 0
    for patient in patients:
        if patient.mdph_requests.exists():
            mdph_requests += 1
            # We only look to the last one
            if patient.mdph_requests.order_by('-start_date')[0].start_date < statistic.in_start_date.date():
                mdph_requests_before +=1
    data = []
    data.append(['Dossier avec une demande MDPH', "Dont la dernière demande a été faite avant la période"])
    data.append([(mdph_requests, mdph_requests_before)])
    data_tables.append(data)

    birth_years = dict()
    patients_without_birthyear = []
    for patient in patients:
        try:
            birth_years.setdefault(patient.birthdate.year, []).append(patient)
        except:
            patients_without_birthyear.append(patient)
    data = []
    data.append(['Année de naissance', "Nombre de dossiers", "%"])
    values = []
    for birth_year, pts in birth_years.iteritems():
        values.append((birth_year, len(pts), "%.2f" % (len(pts) / float(len(patients)) * 100)))
    values.append(('Non renseignée',  len(patients_without_birthyear), "%.2f" % (len(patients_without_birthyear) / float(len(patients)) * 100)))
    data.append(values)
    data_tables.append(data)

    if patients_without_birthyear:
        data = []
        data.append(["Patients sans date de naissance"])
        values = [[patients_without_birthyear]]
        data.append(values)
        data_tables.append(data)


    lower_bounds = [0, 3, 5, 7, 11, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 75, 85, 96]
    anap_code = 198
    data = []
    data.append(["Code ANAP", "Tranche d'âge (au %s)" \
        % formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT"),
        "Nombre de dossiers", "%"])
    values = []
    for i in range(len(lower_bounds)):
        lower_bound = lower_bounds[i]
        if i == len(lower_bounds) - 1:
            values.append([anap_code, "De %d ans et plus" % lower_bound, 0, None])
        else:
            values.append([anap_code, "De %d à %d ans" % (lower_bound, lower_bounds[i + 1] - 1), 0, None])
        anap_code += 1
    unknown = 0
    for patient in patients:
        try:
            age = statistic.in_end_date.date() - patient.birthdate
            age = age.days / 365
            i = 0
            while age >= lower_bounds[i+1]:
                i += 1
                if i == len(lower_bounds) - 1:
                    break
            values[i][2] += 1
        except:
            unknown += 1
    for value in values:
        value[3] = "%.2f" % (value[2] / float(len(patients)) * 100)
    values.append(['', "Non renseignée", unknown, "%.2f" % (unknown / float(len(patients)) * 100)])
    data.append(values)
    data_tables.append(data)

    jobs = dict()
    no_job = 0
    for patient in patients:
        job = False
        if patient.job_mother:
            jobs.setdefault(patient.job_mother, []).append(patient)
            job = True
        else:
            for contact in patient.contacts.all():
                if contact.parente and contact.parente.name == 'Mère':
                    if contact.job:
                        jobs.setdefault(contact.job, []).append(patient)
                        job = True
                    break
        if not job:
            no_job += 1
    data = []
    data.append(["Profession de la mère", "Nombre de dossiers", "%"])
    values = []
    for job, pts in jobs.iteritems():
        values.append((job, len(pts), "%.2f" % (len(pts) / float(len(patients)) * 100)))
    values.append(("Non renseignée", no_job, "%.2f" % (no_job / float(len(patients)) * 100)))
    data.append(values)
    data_tables.append(data)

    jobs = dict()
    no_job = 0
    for patient in patients:
        job = False
        if patient.job_father:
            jobs.setdefault(patient.job_father, []).append(patient)
            job = True
        else:
            for contact in patient.contacts.all():
                if contact.parente and contact.parente.name == 'Père':
                    if contact.job:
                        jobs.setdefault(contact.job, []).append(patient)
                        job = True
                    break
        if not job:
            no_job += 1
    data = []
    data.append(["Profession du père", "Nombre de dossiers", "%"])
    values = []
    for job, pts in jobs.iteritems():
        values.append((job, len(pts), "%.2f" % (len(pts) / float(len(patients)) * 100)))
    values.append(("Non renseignée", no_job, "%.2f" % (no_job / float(len(patients)) * 100)))
    data.append(values)
    data_tables.append(data)

    provenances = dict()
    unknown = 0
    for patient in patients:
        if patient.provenance:
            provenances.setdefault(patient.provenance, []).append(patient)
        else:
            unknown += 1
    data = []
    data.append(["Provenances", "Nombre de dossiers", "%"])
    values = []
    for provenance, pts in provenances.iteritems():
        values.append((provenance, len(pts), "%.2f" % (len(pts) / float(len(patients)) * 100)))
    values.append(('Non renseignée', unknown, "%.2f" % (unknown / float(len(patients)) * 100)))
    data.append(values)
    data_tables.append(data)

    outmotives = dict()
    unknown = 0
    for patient in patients:
        if patient.outmotive:
            outmotives.setdefault(patient.outmotive, []).append(patient)
        else:
            unknown += 1
    data = []
    data.append(["Motifs de sortie", "Nombre de dossiers", "%"])
    values = []
    for outmotive, pts in outmotives.iteritems():
        values.append((outmotive, len(pts), "%.2f" % (len(pts) / float(len(patients)) * 100)))
    values.append(('Non renseigné', unknown, "%.2f" % (unknown / float(len(patients)) * 100)))
    data.append(values)
    data_tables.append(data)

    outtos = dict()
    unknown = 0
    for patient in patients:
        if patient.outto:
            outtos.setdefault(patient.outto, []).append(patient)
        else:
            unknown += 1
    data = []
    data.append(["Orientations", "Nombre de dossiers", "%"])
    values = []
    for outto, pts in outtos.iteritems():
        values.append((outto, len(pts), "%.2f" % (len(pts) / float(len(patients)) * 100)))
    values.append(('Non renseigné', unknown, "%.2f" % (unknown / float(len(patients)) * 100)))
    data.append(values)
    data_tables.append(data)

    provenance_places = dict()
    unknown = 0
    for patient in patients:
        if patient.provenanceplace:
            provenance_places.setdefault(patient.provenanceplace, []).append(patient)
        else:
            unknown += 1
    data = []
    data.append(["Lieux de provenance", "Nombre de dossiers", "%"])
    values = []
    for provenance_place, pts in provenance_places.iteritems():
        values.append((provenance_place, len(pts), "%.2f" % (len(pts) / float(len(patients)) * 100)))
    values.append(('Non renseigné', unknown, "%.2f" % (unknown / float(len(patients)) * 100)))
    data.append(values)
    data_tables.append(data)

    return [data_tables]

def acts_synthesis(statistic):
    if not statistic.in_service:
        return None
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)

    data_tables_set = []
    data_tables = []
    data = []
    data.append(['Période', 'Jours',
        "Nombre d'actes proposés sur la période",
        "Dossiers concernés",
        "Nombre d'actes réalisés sur la période",
        "Dossiers concernés"])
    acts = Act.objects.filter(date__gte=statistic.in_start_date,
        date__lte=statistic.in_end_date,
        patient__service=statistic.in_service)
    len_patients = len(set([a.patient.id for a in acts]))
    acts_present = [a for a in acts if a.is_present()]
    len_patients_present = len(set([a.patient.id for a in acts_present]))
    len_acts_present = len(acts_present)
    data.append([("%s - %s"
        % (formats.date_format(statistic.in_start_date, "SHORT_DATE_FORMAT"),
        formats.date_format(statistic.in_end_date, "SHORT_DATE_FORMAT")),
        (statistic.in_end_date-statistic.in_start_date).days+1,
        acts.count(), len_patients, len_acts_present, len_patients_present)])
    data_tables.append(data)
    data_tables_set.append(data_tables)

    data_tables=[]
    acts_types = dict()
    for act in acts:
        acts_types.setdefault(act.act_type, []).append(act)
    data = []
    data.append(["Types des actes", "Nombre d'actes proposés", "Nombre de dossiers", "Nombre d'actes réalisés", "Nombre de dossiers"])
    values = []
    for act_type, acts in sorted(acts_types.items(), key=lambda t: t[0].name):
        values.append((act_type, len(acts), len(set([a.patient.id for a in acts])), len([a for a in acts if a.is_present()]), len(set([a.patient.id for a in acts if a.is_present()]))))
    data.append(values)
    data_tables.append(data)
    data_tables_set.append(data_tables)

    data_tables=[]
    acts_count_participants = dict()
    for act in acts_present:
        acts_count_participants.setdefault(act.doctors.count(), []).append(act)
    data = []
    data.append(["Nombre d'intervenants des actes réalisés", "Nombre d'actes", "Nombre de dossiers concernés"])
    values = []
    for number, acts_counted in acts_count_participants.iteritems():
        values.append((number, len(acts_counted), len(set([a.patient.id for a in acts_counted]))))
    data.append(values)
    data_tables.append(data)
    data_tables_set.append(data_tables)

    for act_type, acts in sorted(acts_types.items(), key=lambda t: t[0].name):
        data_tables=[]
        analysis = {'Non pointés': 0,
            'Reportés': 0, 'Absents': 0, 'Présents': 0}
        for a in acts:
            if a.is_new():
                analysis['Non pointés'] += 1
            elif a.is_absent():
                state = a.get_state()
                if state.state_name == 'REPORTE':
                    analysis['Reportés'] += 1
                else:
                    analysis['Absents'] += 1
            else:
                analysis['Présents'] += 1
        data = []
        data.append(["Type d'acte", act_type])
        values = []
        for status, number in analysis.iteritems():
            values.append((status, number))
        data.append(values)
        data_tables.append(data)
        acts_type_patients = {}
        for act in acts:
            acts_type_patients.setdefault(act.patient, []).append(act)
        data = []
        data.append(["Patient", "Actes proposés", "Actes réalisés"])
        values = []
        for patient, acts_type in acts_type_patients.iteritems():
            values.append((patient, len(acts_type), len([a for a in acts_type if a.is_present()])))
        data.append(values)
        data_tables.append(data)
        data_tables_set.append(data_tables)

    return data_tables_set

def acts_synthesis_cmpp(statistic):
    data_tables_set = []
    if not statistic.in_service:
        return None
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    acts = Act.objects.filter(date__gte=statistic.in_start_date,
        date__lte=statistic.in_end_date,
        patient__service=statistic.in_service)
    acts_billed = acts.filter(is_billed=True)
    patients_billed = dict()
    for act in acts_billed:
        patients_billed.setdefault(act.patient, [False, False])
        if act.get_hc_tag() and act.get_hc_tag()[0] == 'D':
            patients_billed[act.patient][0] = True
        elif act.get_hc_tag() and act.get_hc_tag()[0] == 'T':
            patients_billed[act.patient][1] = True
    values1, values2, values3 = [], [], []
    for patient, vals in patients_billed.iteritems():
        pfields = [patient.last_name, patient.first_name, patient.paper_id]
        if vals == [True, False]:
            values1.append(pfields)
        elif vals == [False, True]:
            values2.append(pfields)
        elif vals == [True, True]:
            values3.append(pfields)
    cols = ['Nom', 'Prénom', 'Numéro de dossier']
    data_tables_set.append([[['Seulement facturé en diagnostic'], [[len(values1)]]], [cols, sorted(values1, key=lambda t: t[0])]])
    data_tables_set.append([[['Seulement facturé en traitement'], [[len(values2)]]], [cols, sorted(values2, key=lambda t: t[0])]])
    data_tables_set.append([[['Facturé en diagnostic et en traitement'], [[len(values3)]]], [cols, sorted(values3, key=lambda t: t[0])]])
    return data_tables_set

def mises(statistic):
    if not statistic.in_service:
        return None
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    acts = Act.objects.filter(valide='True',
        date__gte=statistic.in_start_date,
        date__lte=statistic.in_end_date,
        patient__service=statistic.in_service)
    patients = acts.order_by('patient').distinct('patient').\
        values_list('patient')
    patients = PatientRecord.objects.filter(id__in=[patient[0]
        for patient in patients])
    pathologies = dict()
    for patient in patients:
        for pathology in patient.mises_1.all():
            pathologies.setdefault(pathology, 0)
            pathologies[pathology] += 1
        for pathology in patient.mises_2.all():
            pathologies.setdefault(pathology, 0)
            pathologies[pathology] += 1
        for pathology in patient.mises_3.all():
            pathologies.setdefault(pathology, 0)
            pathologies[pathology] += 1
    data = [['Pathologies MISES', 'Nombre de patients concernés']]
    data.append(OrderedDict(sorted(pathologies.items(), key=lambda t: t[0].ordering_code)).items())
    return [[data]]

def deficiencies(statistic):
    if not statistic.in_service:
        return None
    if not statistic.in_end_date:
        statistic.in_end_date = datetime.today()
    if not statistic.in_start_date:
        statistic.in_start_date = datetime(statistic.in_end_date.year, 1, 1)
    acts = Act.objects.filter(valide='True',
        date__gte=statistic.in_start_date,
        date__lte=statistic.in_end_date,
        patient__service=statistic.in_service)
    patients = acts.order_by('patient').distinct('patient').\
        values_list('patient')
    patients = PatientRecord.objects.filter(id__in=[patient[0]
        for patient in patients])
    deficiencies_three = ('deficiency_intellectual',
            'deficiency_autism_and_other_ted',
            'deficiency_mental_disorder', 'deficiency_learning_disorder',
            'deficiency_auditory', 'deficiency_visual', 'deficiency_motor',
            'deficiency_metabolic_disorder', 'deficiency_brain_damage',
            'deficiency_behavioral_disorder', 'deficiency_other_disorder')
    data = [['Déficiences', 'Nombre de patients concernés'], []]
    for deficiency in deficiencies_three:
        name = PatientRecord._meta.get_field_by_name(deficiency)[0].verbose_name
        filter_dict = {deficiency: 1}
        data[1].append((name + ' à titre principal', patients.filter(**filter_dict).count()))
        filter_dict = {deficiency: 2}
        data[1].append((name + ' à titre associé', patients.filter(**filter_dict).count()))
    name = PatientRecord._meta.get_field_by_name('deficiency_polyhandicap')[0].verbose_name
    data[1].append((name, patients.filter(deficiency_polyhandicap=True).count()))
    name = PatientRecord._meta.get_field_by_name('deficiency_in_diagnostic')[0].verbose_name
    data[1].append((name, patients.filter(deficiency_in_diagnostic=True).count()))
    return [[data]]

class Statistic(object):
    in_start_date = None
    in_end_date = None
    in_service = None
    in_participants = None
    in_patients = None
    in_year = None
    inscriptions = False

    def __init__(self, name=None, inputs=dict()):
        self.name = name
        params = STATISTICS.get(name, {})
        self.display_name = params['display_name']
        self.category = params['category']
        self.inputs = inputs
        self.in_participants = list()
        participants = inputs.get('participants')
        if participants:
            p_str_ids = [p for p in participants.split('|') if p]
            for str_id in p_str_ids:
                try:
                    self.in_participants.append(Worker.objects.get(pk=int(str_id)))
                except:
                    pass
        self.in_patients = list()
        patients = inputs.get('patients')
        if patients:
            p_str_ids = [p for p in patients.split('|') if p]
            for str_id in p_str_ids:
                try:
                    self.in_patients.append(PatientRecord.objects.get(pk=int(str_id)))
                except:
                    pass
        self.in_service = inputs.get('service')
        self.in_start_date = None
        try:
            self.in_start_date = datetime.strptime(inputs.get('start_date'),
                "%d/%m/%Y")
            self.in_year = self.in_start_date.year
        except:
            pass
        self.in_end_date = None
        try:
            self.in_end_date = datetime.strptime(inputs.get('end_date'),
                "%d/%m/%Y")
        except:
            pass
        self.inscriptions = inputs.get('inscriptions')

    def get_data(self):
        func = globals()[self.name]
        data = func(self)
        self.data = [[[["Date du jour", "Service", "Nom statistique"],
            [[formats.date_format(datetime.today(), "SHORT_DATE_FORMAT"),
            self.in_service, STATISTICS[self.name]['display_name']]]]]] + data
        return self.data

    def render_to_csv(self):
        _delimiter = ';'
        _quotechar = '|'
        _doublequote = True
        _skipinitialspace = False
        _lineterminator = '\r\n'
        _quoting = csv.QUOTE_MINIMAL
        if getattr(settings, 'CSVPROFILE', None):
            csv_profile = settings.CSVPROFILE
            _delimiter = csv_profile.get('delimiter', ';')
            _quotechar = csv_profile.get('quotechar', '|')
            _doublequote = csv_profile.get('doublequote', True)
            _skipinitialspace = csv_profile.get('skipinitialspace', False)
            _lineterminator = csv_profile.get('lineterminator', '\r\n')
            _quoting = csv_profile.get('quoting', csv.QUOTE_MINIMAL)
        class CSVProfile(csv.Dialect):
            delimiter = _delimiter
            quotechar = _quotechar
            doublequote = _doublequote
            skipinitialspace = _skipinitialspace
            lineterminator = _lineterminator
            quoting = _quoting
        csv.register_dialect('csv_profile', CSVProfile())
        encoding = getattr(settings, 'CSV_ENCODING', 'utf-8')

        import codecs
        filename = None
        with tempfile.NamedTemporaryFile(delete=False) as temp_out_csv:
            filename = temp_out_csv.name
            temp_out_csv.close()
        with codecs.open(filename, 'w+b', encoding=encoding) as encoded_f:
            try:
                writer = csv.writer(encoded_f, dialect='csv_profile')
                for data_set in self.data:
                    for data in data_set:
                        writer.writerow(data[0])
                        if len(data) > 1:
                            for d in data[1]:
                                writer.writerow(d)
                        writer.writerow([])
                    writer.writerow([])
                return filename
            except:
                try:
                    os.unlink(temp_out_pdf.name)
                except:
                    pass

    def get_file(self):
        self.get_data()
        return self.render_to_csv()
