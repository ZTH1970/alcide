# -*- coding: utf-8 -*-
import os
import tempfile
import csv

from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Count

from calebasse.dossiers.models import PatientRecord
from calebasse.personnes.models import Worker
from calebasse.actes.models import Act


STATISTICS = {
    'patients_per_worker_for_period' :
        {
        'display_name': 'Liste des enfants suivis par intervenant sur une '
            'période',
        'category': 'Suivi'
    },
    'annual_activity' :
        {
        'display_name': "Tableaux de l'activité annuelle",
        'category': 'Synthèse'
    },
}


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


def annual_activity(statistic):
    rows = ['total', 'pointe', 'non_pointe', 'absent', 'percent_abs', 'reporte', 'acts_present', 'abs_non_exc', 'abs_exc', 'abs_inter', 'annul_nous', 'annul_famille', 'abs_ess_pps', 'enf_hosp', 'non_facturables', 'facturables', 'perdus', 'doubles', 'really_facturables', 'factures', 'diag', 'trait', 'restants_a_fac', 'refac', 'nf', 'percent_nf', 'patients', 'intervenants', 'days', 'fact_per_day']

    if not statistic.in_service:
        return None

    # One table for all intervene and one per intervene (selected or all)
    end_day = datetime.today()
    start_day = datetime(end_day.year, 1, 1)
    if statistic.in_year:
        end_day = datetime(statistic.in_year, 12, 31)
        start_day = datetime(statistic.in_year, 1, 1)
    rd = relativedelta(months=1)
    analyses = {'global': []}
    trim_cnt = 0
    for i in range(0, 12):
        sd = start_day + i * rd
        ed = sd + rd
        if ed > end_day:
            ed = end_day
        acts = Act.objects.filter(date__gte=sd.date(),
            date__lt=ed.date(), patient__service=statistic.in_service)
        analyses['global'].append(AnnualActivityProcessingColumn())
        analyses['global'][i+trim_cnt].patients = acts.aggregate(Count('patient', distinct=True))['patient__count']
        analyses['global'][i+trim_cnt].intervenants = acts.aggregate(Count('doctors', distinct=True))['doctors__count']
        analyses['global'][i+trim_cnt].days = acts.aggregate(Count('date', distinct=True))['date__count']
        for a in acts:
            if a.is_new():
                analyses['global'][i+trim_cnt].non_pointe += 1
            elif a.is_absent():
                state = a.get_state()
                if state.state_name == 'REPORTE':
                    analyses['global'][i+trim_cnt].reporte += 1
                else:
                    analyses['global'][i+trim_cnt].absent += 1
                    if state.state_name == 'ABS_NON_EXC':
                        analyses['global'][i+trim_cnt].abs_non_exc += 1
                    elif state.state_name == 'ABS_EXC':
                        analyses['global'][i+trim_cnt].abs_exc += 1
                    elif state.state_name == 'ABS_INTER':
                        analyses['global'][i+trim_cnt].abs_inter += 1
                    elif state.state_name == 'ANNUL_NOUS':
                        analyses['global'][i+trim_cnt].annul_nous += 1
                    elif state.state_name == 'ANNUL_FAMILLE':
                        analyses['global'][i+trim_cnt].annul_famille += 1
                    elif state.state_name == 'ABS_ESS_PPS':
                        analyses['global'][i+trim_cnt].abs_ess_pps += 1
                    elif state.state_name == 'ENF_HOSP':
                        analyses['global'][i+trim_cnt].enf_hosp += 1
            else:
                analyses['global'][i+trim_cnt].acts_present += 1
                if statistic.in_service.name == 'CMPP':
                    if not a.is_billable():
                        analyses['global'][i+trim_cnt].non_facturables += 1
                    elif a.is_lost:
                        analyses['global'][i+trim_cnt].perdus += 1
                    elif a.get_state().state_name == 'ACT_DOUBLE':
                        analyses['global'][i+trim_cnt].doubles += 1
                    elif a.is_billed:
                        analyses['global'][i+trim_cnt].factures += 1
                        if a.invoice_set.latest('created').first_tag[0] == 'D':
                            analyses['global'][i+trim_cnt].diag += 1
                        else:
                            analyses['global'][i+trim_cnt].trait += 1
                    else:
                        analyses['global'][i+trim_cnt].restants_a_fac += 1
                        if a.invoice_set.all():
                            analyses['global'][i+trim_cnt].refac += 1

        analyses['global'][i+trim_cnt].total = analyses['global'][i+trim_cnt].non_pointe + analyses['global'][i+trim_cnt].reporte + analyses['global'][i+trim_cnt].absent + analyses['global'][i+trim_cnt].acts_present
        analyses['global'][i+trim_cnt].pointe = analyses['global'][i+trim_cnt].total - analyses['global'][i+trim_cnt].non_pointe
        percent_abs = 100
        if not analyses['global'][i+trim_cnt].pointe:
            percent_abs = 0
        elif analyses['global'][i+trim_cnt].absent:
            percent_abs = (analyses['global'][i+trim_cnt].absent/float(analyses['global'][i+trim_cnt].pointe))*100
        analyses['global'][i+trim_cnt].percent_abs = "%.2f" % percent_abs

        if statistic.in_service.name == 'CMPP':
            analyses['global'][i+trim_cnt].facturables = analyses['global'][i+trim_cnt].acts_present - analyses['global'][i+trim_cnt].non_facturables
            analyses['global'][i+trim_cnt].really_facturables = analyses['global'][i+trim_cnt].facturables - analyses['global'][i+trim_cnt].perdus - analyses['global'][i+trim_cnt].doubles
            analyses['global'][i+trim_cnt].nf = analyses['global'][i+trim_cnt].perdus + analyses['global'][i+trim_cnt].doubles + analyses['global'][i+trim_cnt].non_facturables # + analyses['global'][i+trim_cnt].reporte
            percent_nf = 100
            if not analyses['global'][i+trim_cnt].pointe:
                percent_nf = 0
            elif analyses['global'][i+trim_cnt].nf:
                percent_nf = (analyses['global'][i+trim_cnt].nf/float(analyses['global'][i+trim_cnt].pointe))*100
            analyses['global'][i+trim_cnt].percent_nf = "%.2f" % percent_nf
            if analyses['global'][i+trim_cnt].days:
                analyses['global'][i+trim_cnt].fact_per_day = "%.1f" % (analyses['global'][i+trim_cnt].really_facturables / analyses['global'][i+trim_cnt].days)

        if not (i + 1) % 3:
            analyses['global'].append(AnnualActivityProcessingColumn())
            trim_cnt += 1
            for row in rows:
                if row == 'percent_abs':
                    pointe = analyses['global'][i+trim_cnt-1].pointe + analyses['global'][i-2+trim_cnt].pointe + analyses['global'][i-3+trim_cnt].pointe
                    tot_abs = analyses['global'][i+trim_cnt-1].absent + analyses['global'][i-2+trim_cnt].absent + analyses['global'][i-3+trim_cnt].absent
                    percent_abs = 100
                    if not pointe:
                        percent_abs = 0
                    elif tot_abs:
                        percent_abs = (tot_abs/float(pointe))*100
                    analyses['global'][i+trim_cnt].percent_abs = "%.2f" % percent_abs
                elif row == 'percent_nf':
                    pointe = analyses['global'][i+trim_cnt-1].pointe + analyses['global'][i-2+trim_cnt].pointe + analyses['global'][i-3+trim_cnt].pointe
                    tot_nf = analyses['global'][i+trim_cnt-1].nf + analyses['global'][i-2+trim_cnt].nf + analyses['global'][i-3+trim_cnt].nf
                    percent_nf = 100
                    if not pointe:
                        percent_nf = 0
                    elif tot_nf:
                        percent_nf = (tot_nf/float(pointe))*100
                    analyses['global'][i+trim_cnt].percent_nf = "%.2f" % percent_nf
                elif row == 'patients':
                    start = start_day + (i-2) * rd
                    end = sd + 3 * rd
                    if end > end_day:
                        end = end_day
                    acts = Act.objects.filter(date__gte=start.date(),
                        date__lt=end.date(), patient__service=statistic.in_service)
                    analyses['global'][i+trim_cnt].patients = acts.aggregate(Count('patient', distinct=True))['patient__count']
                elif row == 'intervenants':
                    start = start_day + (i-2) * rd
                    end = sd + 3 * rd
                    if end > end_day:
                        end = end_day
                    acts = Act.objects.filter(date__gte=start.date(),
                        date__lt=end.date(), patient__service=statistic.in_service)
                    analyses['global'][i+trim_cnt].intervenants = acts.aggregate(Count('doctors', distinct=True))['doctors__count']
                elif row == 'fact_per_day':
                    if analyses['global'][i+trim_cnt].days:
                        analyses['global'][i+trim_cnt].fact_per_day = "%.1f" % (analyses['global'][i+trim_cnt].really_facturables / analyses['global'][i+trim_cnt].days)
                else:
                    setattr(analyses['global'][i+trim_cnt], row, getattr(analyses['global'][i+trim_cnt-1], row) + getattr(analyses['global'][i-2+trim_cnt], row) + getattr(analyses['global'][i-3+trim_cnt], row))

    analyses['global'].append(AnnualActivityProcessingColumn())
    for row in rows:
        if row == 'percent_abs':
            total = 0
            tot_abs= 0
            for i in (3, 7, 11, 15):
                pointe += analyses['global'][i].pointe
                tot_abs += analyses['global'][i].absent
            percent_abs = 100
            if not pointe:
                percent_abs = 0
            elif tot_abs:
                percent_abs = (tot_abs/float(pointe))*100
            analyses['global'][16].percent_abs = "%.2f" % percent_abs
        elif row == 'percent_nf':
            total = 0
            tot_nf= 0
            for i in (3, 7, 11, 15):
                pointe += analyses['global'][i].pointe
                tot_nf += analyses['global'][i].nf
            percent_nf = 100
            if not pointe:
                percent_nf = 0
            elif tot_nf:
                percent_nf = (tot_nf/float(pointe))*100
            analyses['global'][16].percent_nf = "%.2f" % percent_nf
        elif row == 'patients':
            acts = Act.objects.filter(date__gte=start_day.date(),
                date__lt=end_day.date(), patient__service=statistic.in_service)
            analyses['global'][16].patients = acts.aggregate(Count('patient', distinct=True))['patient__count']
        elif row == 'intervenants':
            acts = Act.objects.filter(date__gte=start_day.date(),
                date__lt=end_day.date(), patient__service=statistic.in_service)
            analyses['global'][16].intervenants = acts.aggregate(Count('doctors', distinct=True))['doctors__count']
        elif row == 'fact_per_day':
            if analyses['global'][16].days:
                analyses['global'][16].fact_per_day = "%.1f" % (analyses['global'][16].really_facturables / analyses['global'][16].days)
        else:
            val = 0
            for i in (3, 7, 11, 15):
                val += getattr(analyses['global'][i], row)
            setattr(analyses['global'][16], row, val)

    data_tables = []
    column_labels = ['Janv', 'Fév', 'Mar', 'T1', 'Avr', 'Mai', 'Jui', 'T2', 'Jui', 'Aoû', 'Sep', 'T3', 'Oct', 'Nov', 'Déc', 'T4', 'Total']

    table_global_main = []
    table_global_main.append(['Tous les intervenants'] + column_labels)
    rows = []
    row = ['Proposés']
    for column in analyses['global']:
        row.append(column.total)
    rows.append(row)
    row = ['Non pointés']
    for column in analyses['global']:
        row.append(column.non_pointe)
    rows.append(row)
    row = ['Absences']
    for column in analyses['global']:
        row.append(column.absent)
    rows.append(row)
    row = ['Reportés']
    for column in analyses['global']:
        row.append(column.reporte)
    rows.append(row)
    row = ['Présents']
    for column in analyses['global']:
        row.append(column.acts_present)
    rows.append(row)
    if statistic.in_service.name == 'CMPP':
        row = ['Facturables']
        for column in analyses['global']:
            row.append(column.really_facturables)
        rows.append(row)
        row = ['Facturés']
        for column in analyses['global']:
            row.append(column.factures)
        rows.append(row)
        row = ['Diagnostics']
        for column in analyses['global']:
            row.append(column.diag)
        rows.append(row)
        row = ['Traitements']
        for column in analyses['global']:
            row.append(column.trait)
        rows.append(row)
        row = ['Restants à facturer']
        for column in analyses['global']:
            row.append(column.restants_a_fac)
        rows.append(row)
        row = ['Dont en refact.']
        for column in analyses['global']:
            row.append(column.refac)
        rows.append(row)
    row = ['Patients']
    for column in analyses['global']:
        row.append(column.patients)
    rows.append(row)
    row = ['Intervenants']
    for column in analyses['global']:
        row.append(column.intervenants)
    rows.append(row)
    row = ['Jours']
    for column in analyses['global']:
        row.append(column.days)
    rows.append(row)
    if statistic.in_service.name == 'CMPP':
        row = ['Fact. / jours']
        for column in analyses['global']:
            row.append(column.fact_per_day)
        rows.append(row)
    table_global_main.append(rows)
    data_tables.append(table_global_main)

    table_global_abs = []
    table_global_abs.append(['Tous (absences)'] + column_labels)
    rows = []
    row = ['Pointés']
    for column in analyses['global']:
        row.append(column.pointe)
    rows.append(row)
    row = ['Absences']
    for column in analyses['global']:
        row.append(column.absent)
    rows.append(row)
    row = ['% absences / pointés']
    for column in analyses['global']:
        row.append(column.percent_abs)
    rows.append(row)
    row = ['Excusées']
    for column in analyses['global']:
        row.append(column.abs_exc)
    rows.append(row)
    row = ['Non excusées']
    for column in analyses['global']:
        row.append(column.abs_non_exc)
    rows.append(row)
    row = ["De l'intervenant"]
    for column in analyses['global']:
        row.append(column.abs_inter)
    rows.append(row)
    row = ["Annulés par nous"]
    for column in analyses['global']:
        row.append(column.annul_nous)
    rows.append(row)
    row = ['Annulés par la famille']
    for column in analyses['global']:
        row.append(column.annul_famille)
    rows.append(row)
    row = ['ESS PPS']
    for column in analyses['global']:
        row.append(column.abs_ess_pps)
    rows.append(row)
    row = ['Hospitalisations']
    for column in analyses['global']:
        row.append(column.enf_hosp)
    rows.append(row)
    table_global_abs.append(rows)
    data_tables.append(table_global_abs)

    if statistic.in_service.name == 'CMPP':
        table_global_nf = []
        table_global_nf.append(['Tous (non fact.)'] + column_labels)
        rows = []
        row = ['Pointés']
        for column in analyses['global']:
            row.append(column.pointe)
        rows.append(row)
        row = ['Présents']
        for column in analyses['global']:
            row.append(column.acts_present)
        rows.append(row)
        row = ['De type non fact.']
        for column in analyses['global']:
            row.append(column.non_facturables)
        rows.append(row)
        row = ['De type fact.']
        for column in analyses['global']:
            row.append(column.facturables)
        rows.append(row)
        row = ['Perdus']
        for column in analyses['global']:
            row.append(column.perdus)
        rows.append(row)
        row = ['En doubles']
        for column in analyses['global']:
            row.append(column.doubles)
        rows.append(row)
        row = ['Non facturables']
        for column in analyses['global']:
            row.append(column.nf)
        rows.append(row)
        row = ['% NF / pointés']
        for column in analyses['global']:
            row.append(column.percent_nf)
        rows.append(row)
        table_global_nf.append(rows)
        data_tables.append(table_global_nf)

    return data_tables


def patients_per_worker_for_period(statistic):
    if not (statistic.in_start_date and statistic.in_end_date
            and statistic.in_service):
        return None
    data_tables = []
    data = []
    data.append(['Intervenants', 'Nombre', 'Patients'])
    values = []
    # Get all acts in the period with a patient in the service
    # Make a dic with intervene for keys
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
    return data_tables

class Statistic(models.Model):
    patients = models.ManyToManyField('dossiers.PatientRecord',
            null=True, blank=True, default=None)
    participants = models.ManyToManyField('personnes.People',
            null=True, blank=True, default=None)
    in_start_date = None
    in_end_date = None
    in_service = None
    in_participants = None
    in_patients = None
    in_year = None

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
        except:
            pass
        self.in_end_date = None
        try:
            self.in_end_date = datetime.strptime(inputs.get('end_date'),
                "%d/%m/%Y")
        except:
            pass

    def get_data(self):
        func = globals()[self.name]
        self.data = func(self)
        return self.data

    def render_to_csv(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_out_csv:
            try:
                writer = csv.writer(temp_out_csv, delimiter=';', quotechar='|',
                    quoting=csv.QUOTE_MINIMAL)
                for data in self.data:
                    writer.writerow(data[0])
                    for d in data[1]:
                        writer.writerow(d)
                    writer.writerow([])
                return temp_out_csv.name
            except:
                try:
                    os.unlink(temp_out_pdf.name)
                except:
                    pass

    def get_file(self):
        self.get_data()
        return self.render_to_csv()
