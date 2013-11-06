# -*- coding: utf-8 -*-
import tempfile

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import models
from django.db.models import Max, Q

from model_utils import Choices

from calebasse.dossiers.models import PatientRecord
from calebasse.ressources.models import ServiceLinkedManager, PricePerAct

import list_acts
import progor

from batches import build_batches

def social_security_id_full(nir):
    old = nir
    try:
        # Corse dpt 2A et 2B
        minus = 0
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
        nir = int(nir) - minus
        return old + ' %0.2d' % (97 - (nir % 97))
    except Exception, e:
        return old + ' 00'

def quarter_start_and_end_dates(today=None):
    '''Returns the first and last day of the current quarter'''
    if today is None:
        today = date.today()
    quarter = (today.month - 1) / 3
    start_date = date(day=1, month=((quarter*3) + 1), year=today.year)
    end_date = start_date + relativedelta(months=3) + relativedelta(days=-1)
    return start_date, end_date

class InvoicingManager(ServiceLinkedManager):
    def current_for_service(self, service):
        '''Return the currently open invoicing'''
        if service.name != 'CMPP':
            start_date, end_date = quarter_start_and_end_dates()
            invoicing, created = \
                self.get_or_create(start_date=start_date,
                end_date=end_date, service=service)
            if created:
                invoicing.status = Invoicing.STATUS.closed
                invoicing.save()
        else:
            try:
                invoicing = self.get(service=service,
                        status=Invoicing.STATUS.open)
            except Invoicing.DoesNotExist:
                today = date.today()
                start_date = date(day=today.day, month=today.month, year=today.year)
                invoicing, created = self.get_or_create(service=service,
                    start_date=start_date,
                    status=Invoicing.STATUS.open)
        return invoicing

    def last_for_service(self, service):
        current = self.current_for_service(service)
        last_seq_id = current.seq_id - 1
        try:
            return self.get(service=service,
                seq_id=last_seq_id)
        except:
            return None


def build_invoices_from_acts(acts_diagnostic, acts_treatment):
    invoices = {}
    len_invoices = 0
    len_invoices_hors_pause = 0
    len_acts_invoiced = 0
    len_acts_invoiced_hors_pause = 0
    pricing = PricePerAct.pricing()
    for patient, acts in acts_diagnostic.items():
        invoices[patient] = []
        act, hc = acts[0]
        invoice = dict()
        invoice['ppa'] = pricing.price_at_date(act.date)
        invoice['year'] = act.date.year
        invoice['acts'] = [(act, hc)]
        if len(acts) > 1:
            for act, hc in acts[1:]:
                if invoice['ppa'] != pricing.price_at_date(act.date) or \
                        invoice['year'] != act.date.year:
                    invoices[patient].append(invoice)
                    len_invoices += 1
                    len_acts_invoiced += len(invoice['acts'])
                    if not patient.pause:
                        len_invoices_hors_pause += 1
                        len_acts_invoiced_hors_pause += len(invoice['acts'])
                    invoice = dict()
                    invoice['ppa'] = pricing.price_at_date(act.date)
                    invoice['year'] = act.date.year
                    invoice['acts'] = [(act, hc)]
                else:
                    invoice['acts'].append((act, hc))
        invoices[patient].append(invoice)
        len_invoices += 1
        len_acts_invoiced += len(invoice['acts'])
        if not patient.pause:
            len_invoices_hors_pause += 1
            len_acts_invoiced_hors_pause += len(invoice['acts'])
    pricing = PricePerAct.pricing()
    for patient, acts in acts_treatment.items():
        if not patient in invoices:
            invoices[patient] = []
        act, hc = acts[0]
        invoice = dict()
        invoice['ppa'] = pricing.price_at_date(act.date)
        invoice['year'] = act.date.year
        invoice['acts'] = [(act, hc)]
        if len(acts) > 1:
            for act, hc in acts[1:]:
                if invoice['ppa'] != pricing.price_at_date(act.date) or \
                        invoice['year'] != act.date.year:
                    invoices[patient].append(invoice)
                    len_invoices += 1
                    len_acts_invoiced += len(invoice['acts'])
                    if not patient.pause:
                        len_invoices_hors_pause += 1
                        len_acts_invoiced_hors_pause += len(invoice['acts'])
                    invoice = dict()
                    invoice['ppa'] = pricing.price_at_date(act.date)
                    invoice['year'] = act.date.year
                    invoice['acts'] = [(act, hc)]
                else:
                    invoice['acts'].append((act, hc))
        invoices[patient].append(invoice)
        len_invoices += 1
        len_acts_invoiced += len(invoice['acts'])
        if not patient.pause:
            len_invoices_hors_pause += 1
            len_acts_invoiced_hors_pause += len(invoice['acts'])
    return (invoices, len_invoices, len_invoices_hors_pause,
        len_acts_invoiced, len_acts_invoiced_hors_pause)

# The firts cmpp invoicing with calebasse
INVOICING_OFFSET = 134

class Invoicing(models.Model):
    '''Represent a batch of invoices:

       end_date - only acts before this date will be considered
       status   - current status of the invoicing
       acts     - acts bounded to this invoicing when the invoicing is validated

       STATUS - the possible status:
        - open, the invoicing is open for new acts
        - closed, invoicing has been closed, no new acts will be accepted after
          the end_date,
        - validated,
    '''
    STATUS = Choices('open', 'closed', 'validated', 'sent')

    seq_id = models.IntegerField(blank=True, null=True)

    service = models.ForeignKey('ressources.Service', on_delete='PROTECT')

    start_date = models.DateField(
            verbose_name=u'Ouverture de la facturation')

    end_date = models.DateField(
            verbose_name=u'Clôturation de la facturation',
            blank=True,
            null=True)

    status = models.CharField(
            verbose_name=u'Statut',
            choices=STATUS,
            default=STATUS.open,
            max_length=20)

    acts = models.ManyToManyField('actes.Act')

    objects = InvoicingManager()

    class Meta:
        unique_together = (('seq_id', 'service'),)

    def allocate_seq_id(self):
        '''Allocate a new sequence id for a new invoicing.'''
        seq_id = 1
        max_seq_id = Invoicing.objects.for_service(self.service) \
                .aggregate(Max('seq_id'))['seq_id__max']
        if not max_seq_id:
            if self.service.name == 'CMPP':
                seq_id = INVOICING_OFFSET
        else:
            seq_id = max_seq_id + 1
        return seq_id

    def list_for_billing(self):
        '''Return the acts candidates for billing'''
        if self.service.name == 'CMPP':
            end_date = self.end_date
            if not end_date:
                today = date.today()
                end_date = date(day=today.day, month=today.month, year=today.year)
            return list_acts.list_acts_for_billing_CMPP(end_date,
                    service=self.service)
        elif self.service.name == 'CAMSP':
            return list_acts.list_acts_for_billing_CAMSP(self.start_date,
                    self.end_date, service=self.service)
        elif 'SESSAD' in self.service.name:
            return list_acts.list_acts_for_billing_SESSAD(self.start_date,
                    self.end_date, service=self.service)
        else:
            raise RuntimeError('Unknown service', self.service)

    def get_batches(self):
        batches = list()
        for hc, bs in build_batches(self).iteritems():
            for batch in bs:
                amount_rejected = sum([invoice.decimal_amount
                    for invoice in batch.invoices
                    if invoice.rejected])
                versement = batch.total - amount_rejected
                batches.append((hc, batch, amount_rejected, versement))
        return batches

    def get_stats_per_price_per_year(self):
        stats_final = dict()
        stats_final['total'] = (0, 0)
        stats_final['detail'] = dict()
        if self.service.name != 'CMPP' or \
                self.status in (Invoicing.STATUS.open,
                Invoicing.STATUS.closed):
            return stats_final
        stats = stats_final['detail']
        invoices = self.invoice_set.all()
        for invoice in invoices:
            if not invoice.list_dates:
                continue
            # All acts of an invoice are the same year and at the same price
            dates = invoice.list_dates.split('$')
            year = datetime.strptime(dates[0], "%d/%m/%Y").year
            ppa = invoice.decimal_ppa
            if year not in stats:
                stats[year] = dict()
            if ppa not in stats[year]:
                stats[year][ppa] = (0, 0)
            nb_acts, amount = stats[year][ppa]
            nb_acts += len(dates)
            amount += invoice.decimal_amount
            stats[year][ppa] = (nb_acts, amount)
            nb_acts_f, amount_f = stats_final['total']
            nb_acts_f += invoice.acts.count()
            amount_f += invoice.decimal_amount
            stats_final['total'] = (nb_acts_f, amount_f)
        return stats_final

    def get_stats_or_validate(self, commit=False):
        '''
            If the invoicing is in state open or closed and commit is False
                Return the stats of the billing
            If the invoicing is in state open or closed and commit is True
                Proceed to invoices creation, healthcare charging, acts as billed
                Return the stats of the billing
            If the invoicing is in state validated or sent
                Return the stats of the billing
        '''
        days_not_locked = 0
        if self.service.name == 'CMPP':
            if self.status in (Invoicing.STATUS.open,
                    Invoicing.STATUS.closed):
                '''
                    The stats are build dynamiccaly according to the
                    acts billable and the healthcares
                '''
                (acts_not_locked, days_not_locked, acts_not_valide,
                    acts_not_billable, acts_pause, acts_diagnostic,
                    acts_treatment, acts_losts,
                    acts_losts_missing_policy,
                    acts_losts_missing_birthdate) = \
                        self.list_for_billing()

                (invoices, len_invoices, len_invoices_hors_pause,
                    len_acts_invoiced, len_acts_invoiced_hors_pause) = \
                        build_invoices_from_acts(acts_diagnostic, acts_treatment)
                len_patient_invoiced = len(invoices.keys())
                len_patient_invoiced_hors_pause = 0
                for patient in invoices.keys():
                    if not patient.pause:
                        len_patient_invoiced_hors_pause = len_patient_invoiced_hors_pause + 1

                patients = set(acts_not_locked.keys() + acts_not_valide.keys() + \
                    acts_not_billable.keys() + acts_diagnostic.keys() + acts_treatment.keys() + \
                    acts_losts.keys() + acts_pause.keys() + acts_losts_missing_policy.keys() + \
                    acts_losts_missing_birthdate.keys())

                patients_stats = []
                len_patient_with_lost_acts = 0
                len_acts_lost = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                len_patient_with_lost_acts_missing_policy = 0
                len_acts_losts_missing_policy = 0
                len_patient_with_lost_acts_missing_birthdate = 0
                len_acts_losts_missing_birthdate = 0
                batches = {}
                last_batch = {}
                for patient in patients:
                    dic = {}
                    if patient in invoices.keys():
                        dic['invoices'] = invoices[patient]
                        if commit and not patient.pause:
                            policy_holder = patient.policyholder
                            try:
                                address = unicode(policy_holder.addresses.filter(place_of_life=True)[0])
                            except:
                                try:
                                    address = unicode(policy_holder.addresses.all()[0])
                                except:
                                    address = u''
                            invoice_kwargs = dict(
                                    patient_id=patient.id,
                                    patient_last_name=patient.last_name,
                                    patient_first_name=patient.first_name,
                                    patient_social_security_id=patient.social_security_id or '',
                                    patient_birthdate=patient.birthdate,
                                    patient_twinning_rank=patient.twinning_rank,
                                    patient_healthcenter=patient.health_center,
                                    patient_other_health_center=patient.other_health_center or '',
                                    patient_entry_date=patient.entry_date,
                                    patient_exit_date=patient.exit_date,
                                    policy_holder_id=policy_holder.id,
                                    policy_holder_last_name=policy_holder.last_name,
                                    policy_holder_first_name=policy_holder.first_name,
                                    policy_holder_social_security_id=policy_holder.social_security_id,
                                    policy_holder_other_health_center=policy_holder.other_health_center or '',
                                    policy_holder_healthcenter=policy_holder.health_center,
                                    policy_holder_address=address)
                            for invoice in invoices[patient]:
                                ppa = invoice['ppa'] * 100
                                acts = invoice['acts']
                                amount = ppa * len(acts)
                                list_dates = '$'.join([act.date.strftime('%d/%m/%Y') for act, hc in acts])
                                in_o = Invoice(
                                        invoicing=self,
                                        ppa=ppa,
                                        amount=amount,
                                        list_dates = list_dates,
                                        **invoice_kwargs)
                                in_o.save()
                                for act, hc in acts:
                                    act.is_billed = True
                                    act.healthcare = hc
                                    act.save()
                                    in_o.acts.add(act)
                                in_o.first_tag = acts[0][0].get_hc_tag()
                                in_o.save()

                                # calcule le numero de lot pour cette facture
                                hc = in_o.health_center
                                hc_dest = hc.hc_invoice or hc
                                dest = hc_dest.large_regime.code + ' ' + hc_dest.dest_organism
                                if dest not in batches:
                                    batches[dest] = {}
                                if hc not in batches[dest]:
                                    nb1 = Invoice.objects.new_batch_number(health_center=hc_dest, invoicing=self)
                                    nb2 = Invoice.objects.new_batch_number(health_center=hc, invoicing=self)
                                    nb = max(nb1, nb2, last_batch.get(dest,0) + 1)
                                    last_batch[dest] = nb
                                    batches[dest][hc] = [{ 'batch': nb, 'size': 2, 'invoices': [], }]
                                # pas plus de 950 lignes par lot (le fichier B2 final ne doit
                                # pas depasser 999 lignes au total) :
                                b = batches[dest][hc].pop()
                                b2_size = in_o.acts.count() + 2
                                if (b['size'] + b2_size) > 950:
                                    batches[dest][hc].append(b)
                                    nb = last_batch.get(dest, 0) + 1
                                    last_batch[dest] = nb
                                    b = {'batch': nb, 'size': 2, 'invoices': []}
                                b['invoices'].append(in_o)
                                b['size'] += b2_size
                                batches[dest][hc].append(b)

                                in_o.batch = b['batch']
                                in_o.save()

                            pass
                    if patient in acts_losts.keys():
                        # TODO: More details about healthcare
                        dic['losts'] = acts_losts[patient]
                        len_patient_with_lost_acts += 1
                        len_acts_lost += len(acts_losts[patient])
                    if patient in acts_pause.keys():
                        dic['acts_paused'] = acts_pause[patient]
                        len_patient_acts_paused += 1
                        len_acts_paused += len(acts_pause[patient])
                    if patient in acts_losts_missing_policy.keys():
                        # TODO: More details about healthcare
                        dic['losts_missing_policy'] = acts_losts_missing_policy[patient]
                        len_patient_with_lost_acts_missing_policy += 1
                        len_acts_losts_missing_policy += len(acts_losts_missing_policy[patient])
                    if patient in acts_losts_missing_birthdate.keys():
                        dic['losts_missing_birthdate'] = acts_losts_missing_birthdate[patient]
                        len_patient_with_lost_acts_missing_birthdate += 1
                        len_acts_losts_missing_birthdate += len(acts_losts_missing_birthdate[patient])
                    if dic:
                        patients_stats.append((patient, dic))
                patients_stats = sorted(patients_stats, key=lambda patient: (patient[0].last_name, patient[0].first_name))

                len_patients = len(patients_stats)

                if commit:
                    self.status = Invoicing.STATUS.validated
                    self.save()

            else:
                '''
                    Grab stats from the invoices
                '''
                len_patients = 0
                len_invoices = 0
                len_acts_invoiced = 0
                patients_stats = {}
                days_not_locked = []
                invoices = self.invoice_set.all()
                patients = {}
                for invoice in invoices:
                    len_invoices = len_invoices + 1
                    if invoice.list_dates:
                        len_acts_invoiced += len(invoice.list_dates.split('$'))
                    patient = None
                    if not invoice.patient_id in patients.keys():
                        try:
                            patient = PatientRecord.objects.get(id=invoice.patient_id)
                        except:
                            patient = PatientRecord(last_name=invoice.patient_last_name, first_name=invoice.patient_first_name)
                        patients[invoice.patient_id] = patient
                        len_patients = len_patients + 1
                        patients_stats[patient] = {}
                        patients_stats[patient]['invoices'] = []
                    else:
                        patient = patients[invoice.patient_id]
                    patients_stats[patient]['invoices'].append(invoice)
                patients_stats = sorted(patients_stats.items(), key=lambda patient: (patient[0].last_name, patient[0].first_name))
                # all patients in the invoicing are invoiced
                len_patient_invoiced = 0
                # These stats are not necessary because excluded form the validated invoicing
                len_invoices_hors_pause = 0
                len_acts_invoiced_hors_pause = 0
                len_patient_invoiced_hors_pause = 0
                len_acts_lost = 0
                len_patient_with_lost_acts = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                len_patient_with_lost_acts_missing_policy = 0
                len_acts_losts_missing_policy = 0
                len_patient_with_lost_acts_missing_birthdate = 0
                len_acts_losts_missing_birthdate = 0
            return (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused, len_acts_losts_missing_policy,
                len_patient_with_lost_acts_missing_policy,
                len_acts_losts_missing_birthdate,
                len_patient_with_lost_acts_missing_birthdate)
        elif self.service.name == 'CAMSP':
            if self.status in Invoicing.STATUS.closed:
                (acts_not_locked, days_not_locked, acts_not_valide,
                acts_not_billable, acts_pause, acts_bad_state,
                acts_accepted, patients_missing_policy) = self.list_for_billing()
                len_patient_pause = 0
                len_patient_hors_pause = 0
                len_acts_pause = 0
                len_acts_hors_pause = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                patients = set(acts_accepted.keys() + acts_pause.keys())
                patients_stats = []
                for patient in patients:
                    dic = {}
                    if patient in acts_accepted.keys():
                        acts = acts_accepted[patient]
                        dic['accepted'] = acts
                        if patient.pause:
                            len_patient_pause += 1
                            len_acts_pause += len(acts)
                        else:
                            len_patient_hors_pause += 1
                            len_acts_hors_pause += len(acts)
                            if commit:
                                policy_holder = patient.policyholder
                                try:
                                    address = unicode(policy_holder.addresses.filter(place_of_life=True)[0])
                                except:
                                    try:
                                        address = unicode(policy_holder.addresses.all()[0])
                                    except:
                                        address = u''
                                invoice_kwargs = dict(
                                        patient_id=patient.id,
                                        patient_last_name=patient.last_name,
                                        patient_first_name=patient.first_name,
                                        patient_social_security_id=patient.social_security_id or '',
                                        patient_birthdate=patient.birthdate,
                                        patient_twinning_rank=patient.twinning_rank,
                                        patient_healthcenter=patient.health_center,
                                        patient_other_health_center=patient.other_health_center or '',
                                        patient_entry_date=patient.entry_date,
                                        patient_exit_date=patient.exit_date,
                                        policy_holder_id=policy_holder.id,
                                        policy_holder_last_name=policy_holder.last_name,
                                        policy_holder_first_name=policy_holder.first_name,
                                        policy_holder_social_security_id=policy_holder.social_security_id or '',
                                        policy_holder_other_health_center=policy_holder.other_health_center or '',
                                        policy_holder_healthcenter=policy_holder.health_center,
                                        policy_holder_address=address)
                                if policy_holder.management_code:
                                    management_code = policy_holder.management_code
                                    invoice_kwargs['policy_holder_management_code'] = management_code.code
                                    invoice_kwargs['policy_holder_management_code_name'] = management_code.name
                                list_dates = '$'.join([act.date.strftime('%d/%m/%Y') for act in acts])
                                invoice = Invoice(
                                        invoicing=self,
                                        ppa=0, amount=0,
                                        list_dates=list_dates,
                                        **invoice_kwargs)
                                invoice.save()
                                for act in acts:
                                    act.is_billed = True
                                    act.save()
                                    invoice.acts.add(act)
                    if patient in acts_pause.keys():
                        dic['acts_paused'] = acts_pause[patient]
                        len_patient_acts_paused += 1
                        len_acts_paused += len(acts_pause[patient])
                    patients_stats.append((patient, dic))
                patients_stats = sorted(patients_stats, key=lambda patient: (patient[0].last_name, patient[0].first_name))
                if commit:
                    self.status = Invoicing.STATUS.validated
                    self.save()
            else:
                patients_stats = {}
                len_patient_pause = 0
                len_patient_hors_pause = 0
                len_acts_pause = 0
                len_acts_hors_pause = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                days_not_locked = []
                patients_missing_policy = []
                invoices = self.invoice_set.all()
                for invoice in invoices:
                    len_patient_hors_pause += 1
                    if invoice.list_dates:
                        len_acts_hors_pause += len(invoice.list_dates.split('$'))
                    patient = None
                    try:
                        patient = PatientRecord.objects.get(id=invoice.patient_id)
                    except:
                        patient = PatientRecord(last_name=invoice.patient_last_name, first_name=invoice.patient_first_name)
                    patients_stats[patient] = {}
                    patients_stats[patient]['accepted'] = invoice.acts.all()
                patients_stats = sorted(patients_stats.items(), key=lambda patient: (patient[0].last_name, patient[0].first_name))
            return (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused, patients_missing_policy)
        else:
            if self.status in Invoicing.STATUS.closed:
                (acts_not_locked, days_not_locked, acts_not_valide,
                acts_not_billable, acts_pause, acts_bad_state,
                acts_missing_valid_notification, acts_accepted,
                patients_missing_policy) = \
                    self.list_for_billing()

                len_patient_pause = 0
                len_patient_hors_pause = 0
                len_acts_pause = 0
                len_acts_hors_pause = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                len_patient_missing_notif = 0
                len_acts_missing_notif = 0
                patients = set(acts_accepted.keys() + \
                    acts_missing_valid_notification.keys() + \
                    acts_pause.keys())
                patients_stats = []
                patients_missing_notif = []
                for patient in patients:
                    dic = {}
                    acts_to_commit = []
                    if patient in acts_accepted.keys():
                        acts = acts_accepted[patient]
                        acts_to_commit.extend(acts)
                        dic['accepted'] = acts
                        if patient.pause:
                            len_patient_pause += 1
                            len_acts_pause += len(acts)
                        else:
                            len_patient_hors_pause += 1
                            len_acts_hors_pause += len(acts)
                    if patient in acts_missing_valid_notification.keys():
                        patients_missing_notif.append(patient)
                        acts = acts_missing_valid_notification[patient]
                        acts_to_commit.extend(acts)
                        dic['missings'] = acts
                        len_patient_missing_notif += 1
                        len_acts_missing_notif += len(acts)
                        if patient.pause:
                            if not 'accepted' in dic:
                                len_patient_pause += 1
                            len_acts_pause += len(acts)
                        else:
                            if not 'accepted' in dic:
                                len_patient_hors_pause += 1
                            len_acts_hors_pause += len(acts)
                    if commit and acts_to_commit:
                        policy_holder = patient.policyholder
                        try:
                            address = unicode(policy_holder.addresses.filter(place_of_life=True)[0])
                        except:
                            try:
                                address = unicode(policy_holder.addresses.all()[0])
                            except:
                                address = u''
                        invoice_kwargs = dict(
                                patient_id=patient.id,
                                patient_last_name=patient.last_name,
                                patient_first_name=patient.first_name,
                                patient_social_security_id=patient.social_security_id or '',
                                patient_birthdate=patient.birthdate,
                                patient_twinning_rank=patient.twinning_rank,
                                patient_healthcenter=patient.health_center,
                                patient_other_health_center=patient.other_health_center or '',
                                patient_entry_date=patient.entry_date,
                                patient_exit_date=patient.exit_date,
                                policy_holder_id=policy_holder.id,
                                policy_holder_last_name=policy_holder.last_name,
                                policy_holder_first_name=policy_holder.first_name,
                                policy_holder_social_security_id=policy_holder.social_security_id or '',
                                policy_holder_other_health_center=policy_holder.other_health_center or '',
                                policy_holder_healthcenter=policy_holder.health_center,
                                policy_holder_address=address)
                        if policy_holder.management_code:
                            management_code = policy_holder.management_code
                            invoice_kwargs['policy_holder_management_code'] = management_code.code
                            invoice_kwargs['policy_holder_management_code_name'] = management_code.name
                        list_dates = '$'.join([act.date.strftime('%d/%m/%Y') for act in acts_to_commit])
                        invoice = Invoice(
                                invoicing=self,
                                ppa=0, amount=0,
                                list_dates=list_dates,
                                **invoice_kwargs)
                        invoice.save()
                        for act in acts_to_commit:
                            act.is_billed = True
                            act.save()
                            invoice.acts.add(act)
                    if patient in acts_pause.keys():
                        dic['acts_paused'] = acts_pause[patient]
                        len_patient_acts_paused += 1
                        len_acts_paused += len(acts_pause[patient])
                    patients_stats.append((patient, dic))
                patients_stats = sorted(patients_stats, key=lambda patient: (patient[0].last_name, patient[0].first_name))
                if commit:
                    self.status = Invoicing.STATUS.validated
                    self.save()
            else:
                patients_stats = {}
                len_patient_pause = 0
                len_patient_hors_pause = 0
                len_acts_pause = 0
                len_acts_hors_pause = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                len_patient_missing_notif = 0
                len_acts_missing_notif = 0
                days_not_locked = []
                patients_missing_policy = []
                patients_missing_notif = []
                invoices = self.invoice_set.all()
                for invoice in invoices:
                    len_patient_hors_pause += 1
                    if invoice.list_dates:
                        len_acts_hors_pause += len(invoice.list_dates.split('$'))
                    patient = None
                    try:
                        patient = PatientRecord.objects.get(id=invoice.patient_id)
                    except:
                        patient = PatientRecord(last_name=invoice.patient_last_name, first_name=invoice.patient_first_name)
                    patients_stats[patient] = {}
                    patients_stats[patient]['accepted'] = invoice.acts.all()
                patients_stats = sorted(patients_stats.items(), key=lambda patient: (patient[0].last_name, patient[0].first_name))
            return (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause,
                len_patient_missing_notif, len_acts_missing_notif,
                patients_stats, days_not_locked,
                len_patient_acts_paused, len_acts_paused,
                patients_missing_policy, patients_missing_notif)

    def save(self, *args, **kwargs):
        if not self.seq_id:
            self.seq_id = self.allocate_seq_id()
        super(Invoicing, self).save(*args, **kwargs)

    def close(self, end_date=None):
        '''Close an open invoicing'''
        if self.service.name != 'CMPP':
            raise RuntimeError('closing Invoicing is only for the CMPP')
        if self.status != Invoicing.STATUS.open:
            raise RuntimeError('closing an un-opened Invoicing')
        if not end_date:
            today = date.today()
            end_date = date(day=today.day, month=today.month, year=today.year)
            if end_date < self.start_date:
                end_date = self.start_date + relativedelta(days=1)
        self.status = Invoicing.STATUS.closed
        self.end_date = end_date
        self.save()
        start_date = self.end_date + relativedelta(days=1)
        invoicing = Invoicing(service=self.service,
            start_date=start_date,
            status=Invoicing.STATUS.open)
        invoicing.save()
        return invoicing

    def export_for_accounting(self):
        '''
            Il faut separer les ecritures pour l'année en cours et les années
            passées.
        '''
        def add_ecriture(health_center, amount):
            accounting_number = '0' + health_center.accounting_number[1:]
            '''Le nom du compte ne devrait pas etre important et seul compter
            le numéro de compte'''
            name = health_center.name
            if len(name) > 30:
                name = name[0:30]
            ecriture = progor.EcritureComptable(date, accounting_number,
                name, cycle, debit=amount)
            imputation = progor.ImputationAnalytique(debit=amount)
            ecriture.add_imputation(imputation)
            journal.add_ecriture(ecriture)
        journal = progor.IdentificationJournal()
        ecritures_current = dict()
        ecritures_past = dict()
        total_current = 0
        total_past = 0
        date = self.end_date.strftime("%d/%m/%Y")
        cycle = str(self.seq_id)
        invoice_year = datetime(self.end_date.year, 1, 1).date()
        for invoice in self.invoice_set.all():
            hc = invoice.health_center.hc_invoice or invoice.health_center
            if invoice.end_date < invoice_year:
                ecritures_past.setdefault(hc, 0)
                ecritures_past[hc] += invoice.amount
                total_past += invoice.amount
            else:
                ecritures_current.setdefault(hc, 0)
                ecritures_current[hc] += invoice.amount
                total_current += invoice.amount
        '''Ce qui est facturé aux caisses est en débit'''
        for health_center, amount in ecritures_past.items():
            add_ecriture(health_center, amount)
        for health_center, amount in ecritures_current.items():
            add_ecriture(health_center, amount)
        '''On équilibre avec du produit en crédit'''
        #Produit années précédentes
        if total_past:
            ecriture = progor.EcritureComptable(date, '77200000',
                'PRODUITS EXERCICES ANTERIEURS', cycle, credit=total_past, type_compte='0')
            imputation = progor.ImputationAnalytique(credit=total_past)
            ecriture.add_imputation(imputation)
            journal.add_ecriture(ecriture)
        #Produit année en cours
        ecriture = progor.EcritureComptable(date, '73130000',
            'PRODUITS EXERCICE', cycle, credit=total_current, type_compte='0')
        imputation = progor.ImputationAnalytique(credit=total_current)
        ecriture.add_imputation(imputation)
        journal.add_ecriture(ecriture)
        content = journal.render()
        service = self.service
        now = datetime.now()
        output_file = tempfile.NamedTemporaryFile(prefix='%s-export-%s-' %
                (service.slug, self.id), suffix='-%s.txt' % now, delete=False)
        output_file.write(content)
        return output_file.name


#class PricePerAct(models.Model):
#    price = models.IntegerField()
#    start_date = models.DateField(
#            verbose_name=u"Prise d'effet",
#            default=date(day=5,month=1,year=1970))
#    end_date = models.DateField(
#            verbose_name=u"Fin d'effet",
#            blank=True,
#            null=True)

#    @classmethod
#    def get_price(cls, at_date=None):
#        if not at_date:
#            at_date = date.today()
#        if isinstance(at_date, datetime):
#            at_date = date(day=at_date.day, month=at_date.month,
#                year=at_date.year)
#        found = cls.objects.filter(start_date__lte = at_date).latest('start_date')
#        if not found:
#            raise Exception('No price to apply')
#        return found.price

#    def __unicode__(self):
#        val = str(self.price) + ' from ' + str(self.start_date)
#        if self.end_date:
#            val = val + ' to ' + str(self.end_date)
#        return val


#def add_price(price, start_date=None):
#    price_o = None
#    ppas = PricePerAct.objects.all()
#    if ppas:
#        if not start_date:
#            raise Exception('A start date is mandatory to add a new Price')
#        last_ppa = PricePerAct.objects.latest('start_date')
#        if last_ppa.start_date >= start_date:
#            raise Exception('The new price cannot apply before the price that currently applies.')
#        if last_ppa.end_date and last_ppa.end_date != (start_date + relativedelta(days=-1)):
#            raise Exception('The new price should apply the day after the last price ends.')
#        last_ppa.end_date = start_date + relativedelta(days=-1)
#        last_ppa.save()
#    if not start_date:
#        price_o = PricePerAct(price=price)
#    else:
#        price_o = PricePerAct(price=price, start_date=start_date)
#    price_o.save()
#    return price_o


PREVIOUS_MAX_BATCH_NUMBERS = {
    'CF00000004001110': 34,
    'CT00000001016421': 1,
    'CT00000001016422': 141,
    'CT00000001025691': 20,
    'CT00000002011011': 8,
    'CT00000002381421': 15,
    'MA00000002381421': 48,

    'SM00000091007381': 98, # faure 43
    'SM00000091007421': 98, # faure 44
    'SM00000091007422': 98, # faure 45
    'SM00000091007431': 98, # faure 46
    'SM00000091007691': 98, # faure 47
    'SM00000091007764': 98, # faure 48

    'SM00000092001422': 14,
    'SM00000092001691': 13,
    'SM00000099038939': 24,
}


class InvoiceManager(models.Manager):
    def new_batch_number(self, health_center, invoicing):
        '''Compute the next batch number for the given health center'''
        global PREVIOUS_MAX_BATCH_NUMBERS
        agg = self \
                .filter(invoicing__service=invoicing.service) \
                .filter(invoicing__seq_id__lt=invoicing.seq_id) \
                .filter(
                    Q(patient_healthcenter=health_center,
                        policy_holder_healthcenter__isnull=True)|
                    Q(policy_holder_healthcenter=health_center)) \
                        .aggregate(Max('batch'))
        max_bn = agg['batch__max']
        if max_bn is None:
            max_bn = PREVIOUS_MAX_BATCH_NUMBERS.get(health_center.b2_000(), 0)
        else:
            max_bn = max(max_bn, PREVIOUS_MAX_BATCH_NUMBERS.get(health_center.b2_000(), 0))
        return max_bn + 1


class Invoice(models.Model):
    objects = InvoiceManager()
    number = models.IntegerField(blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)
    # the patient can be modified (or even deleted) after invoice creation, so
    # we copy his informations here
    patient_id = models.IntegerField(blank=True, null=True)
    patient_last_name = models.CharField(max_length=128,
            verbose_name=u'Nom du patient', default='', blank=True)
    patient_first_name = models.CharField(max_length=128,
            verbose_name=u'Prénom(s) du patient', default='', blank=True)
    patient_social_security_id = models.CharField(max_length=13,
            verbose_name=u"NIR", default='', blank=True)
    patient_birthdate = models.DateField(verbose_name=u"Date de naissance",
            null=True, blank=True)
    patient_twinning_rank = models.IntegerField(
        verbose_name=u"Rang (gémellité)",
        null=True, blank=True)
    patient_healthcenter = models.ForeignKey('ressources.HealthCenter',
            verbose_name=u"Centre d'assurance maladie",
            related_name='related_by_patient_invoices',
            null=True, blank=True)
    patient_entry_date = models.DateField(verbose_name=u'Date d\'entrée du patient',
            blank=True, null=True)
    patient_exit_date = models.DateField(verbose_name=u'Date de sortie du patient',
            blank=True, null=True)
    patient_other_health_center = models.CharField(
        verbose_name=u"Centre spécifique", max_length=4, default='',
        blank=True)
    # policy holder informations
    policy_holder_id = models.IntegerField(blank=True, null=True)
    policy_holder_last_name = models.CharField(max_length=128,
            verbose_name=u'Nom de l\'assuré', default='', blank=True)
    policy_holder_first_name = models.CharField(max_length=128,
            verbose_name=u'Prénom(s) de l\' assuré', default='', blank=True)
    policy_holder_social_security_id = models.CharField(max_length=13,
            verbose_name=u"NIR de l\'assuré", default='', blank=True)
    policy_holder_healthcenter = models.ForeignKey('ressources.HealthCenter',
            verbose_name=u"Centre d'assurance maladie de l\'assuré",
            related_name='related_by_policy_holder_invoices',
            null=True, blank=True)
    policy_holder_other_health_center = models.CharField(
            verbose_name=u"Centre spécifique de l\'assuré", max_length=4,
            default='', blank=True)
    policy_holder_address = models.CharField(max_length=128,
            verbose_name=u'Adresse de l\'assuré', default='', blank=True)
    policy_holder_management_code = models.CharField(max_length=10,
            verbose_name=u'Code de gestion', default='', blank=True)
    policy_holder_management_code_name = models.CharField(max_length=256,
            verbose_name=u'Libellé du code de gestion', default='', blank=True)

    created = models.DateTimeField(u'Création', auto_now_add=True)
    invoicing = models.ForeignKey('facturation.Invoicing',
        on_delete='PROTECT')
    acts = models.ManyToManyField('actes.Act')
    list_dates = models.CharField(max_length=512, blank=True, null=True)
    first_tag = models.CharField(max_length=128, blank=True, null=True)
    amount = models.IntegerField()
    ppa = models.IntegerField()
    rejected = models.BooleanField(verbose_name=u"Rejeté", default=False)

    def save(self, *args, **kwargs):
        if not self.number:
            invoicing = self.invoicing
            self.number = invoicing.seq_id * 1000000 + 1
            max_number = invoicing.invoice_set.aggregate(Max('number'))['number__max']
            if max_number:
                self.number = max_number + 1
        super(Invoice, self).save(*args, **kwargs)

    @property
    def start_date(self):
        res = date.max
        for act in self.acts.all():
            res = min(res, act.date)
        return res

    @property
    def health_center(self):
        return self.policy_holder_healthcenter or self.patient_healthcenter

    @property
    def end_date(self):
        res = date.min
        for act in self.acts.all():
            res = max(res, act.date)
        return res

    @property
    def decimal_amount(self):
        return Decimal(self.amount) / Decimal(100)

    @property
    def decimal_ppa(self):
        return Decimal(self.ppa) / Decimal(100)

    @property
    def kind(self):
        if not self.first_tag:
            return None
        return self.first_tag[0]

    @property
    def patient_social_security_id_full(self):
        if self.patient_social_security_id:
            return social_security_id_full(self.patient_social_security_id)
        else:
            return ''

    @property
    def policy_holder_social_security_id_full(self):
        if self.policy_holder_social_security_id:
            return social_security_id_full(self.policy_holder_social_security_id)
        else:
            return ''

    def __unicode__(self):
        return "Facture %d de %d euros (%d actes)" % (self.number, self.amount, len(self.acts.all()))
