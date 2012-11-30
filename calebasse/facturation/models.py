# -*- coding: utf-8 -*-

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Max

from model_utils import Choices

from calebasse.ressources.models import ServiceLinkedManager

import list_acts

def quarter_start_and_end_dates(today=None):
    '''Returns the first and last day of the current quarter'''
    if today is None:
        today = date.today()
    quarter = today.month / 3
    start_date = date(day=1, month=(quarter*3)+1, year=today.year)
    end_date = start_date + relativedelta(months=3) + relativedelta(days=-1)
    return start_date, end_date

class InvoicingManager(ServiceLinkedManager):
    def current_for_service(self, service):
        '''Return the currently open invoicing'''
        if service.name != 'CMPP':
            start_date, end_date = quarter_start_and_end_dates()
            invoicing, created = self.get_or_create(start_date=start_date,
                    end_date=end_date, service=service)
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
    for patient, acts in acts_diagnostic.items():
        invoices[patient] = []
        act, hc = acts[0]
        invoice = {}
        invoice['ppa'] = PricePerAct.get_price(act.date)
        invoice['year'] = act.date.year
        invoice['acts'] = [(act, hc)]
        for act, hc in acts[1:]:
            if invoice['ppa'] != PricePerAct.get_price(act.date) or \
                    invoice['year'] != act.date.year:
                invoices[patient].append(invoice)
                len_invoices = len_invoices + 1
                len_acts_invoiced = len_acts_invoiced + len(invoice['acts'])
                if not patient.pause:
                    len_invoices_hors_pause = len_invoices_hors_pause + 1
                    len_acts_invoiced_hors_pause = len_acts_invoiced_hors_pause + len(invoice['acts'])
                invoice['ppa'] = PricePerAct.get_price(act.date)
                invoice['year'] = act.date.year
                invoice['acts'] = [(act, hc)]
            else:
                invoice['acts'].append((act, hc))
        invoices[patient].append(invoice)
        len_invoices = len_invoices + 1
        len_acts_invoiced = len_acts_invoiced + len(invoice['acts'])
        if not patient.pause:
            len_invoices_hors_pause = len_invoices_hors_pause + 1
            len_acts_invoiced_hors_pause = len_acts_invoiced_hors_pause + len(invoice['acts'])
    for patient, acts in acts_treatment.items():
        if not patient in invoices:
            invoices[patient] = []
        act, hc = acts[0]
        invoice = {}
        invoice['ppa'] = PricePerAct.get_price(act.date)
        invoice['year'] = act.date.year
        invoice['acts'] = [(act, hc)]
        for act, hc in acts[1:]:
            if invoice['ppa'] != PricePerAct.get_price(act.date) or \
                    invoice['year'] != act.date.year:
                invoices[patient].append(invoice)
                len_invoices = len_invoices + 1
                len_acts_invoiced = len_acts_invoiced + len(invoice['acts'])
                if not patient.pause:
                    len_invoices_hors_pause = len_invoices_hors_pause + 1
                    len_acts_invoiced_hors_pause = len_acts_invoiced_hors_pause + len(invoice['acts'])
                invoice['price'] = PricePerAct.get_price(act.date)
                invoice['year'] = act.date.year
                invoice['acts'] = [(act, hc)]
            else:
                invoice['acts'].append((act, hc))
        invoices[patient].append(invoice)
        len_invoices = len_invoices + 1
        len_acts_invoiced = len_acts_invoiced + len(invoice['acts'])
        if not patient.pause:
            len_invoices_hors_pause = len_invoices_hors_pause + 1
            len_acts_invoiced_hors_pause = len_acts_invoiced_hors_pause + len(invoice['acts'])
    return (invoices, len_invoices, len_invoices_hors_pause,
        len_acts_invoiced, len_acts_invoiced_hors_pause)


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
        if max_seq_id:
            seq_id = seq_id + max_seq_id
        return seq_id

    def list_for_billing(self):
        '''Return the acts candidates for billing'''
        if self.service.name == 'CMPP':
            end_date = self.end_date
            if not end_date:
                today = date.today()
                end_date = date(day=today.day, month=today.month, year=today.year)
            return list_acts.list_acts_for_billing_CMPP_2(end_date,
                    service=self.service)
        elif self.service.name == 'CAMSP':
            return list_acts.list_acts_for_billing_CAMSP(self.start_date,
                    self.end_date, service=self.service)
        elif 'SESSAD' in self.service_name:
            return list_acts.list_acts_for_billing_SESSAD(self.start_date,
                    self.end_date, service=self.service)
        else:
            raise RuntimeError('Unknown service', self.service)

    def get_stats_or_validate(self, commit=False):
        '''
            If the invoicing is in state open or closed and commit is False
                Return the stats of the billing
            If the invoicing is in state open or closed and commit is True
                Proceed to invoices creation, healthcare charging, acts a billed
                Return the stats of the billing
            If the invoicing is in state validated or sent
                Return the stats of the billing

            len_patients: Tous les patients concernés, c'est à dire ayant au moins un acte sur la période, même si absent ou verouillé
            len_invoices: Nombre de factures avec les dossiers en pause qui seraient facturés
            len_invoices_hors_pause: Nombre de factures sans les dossiers en pause
            len_acts_invoiced: Nombre d'actes concernés par les factures avec les dossiers en pause qui seraient facturés
            len_acts_invoiced_hors_pause: Nombre d'actes concernés par les factures sans les dossiers en pause
            len_patient_invoiced: Nombre de patients concernés par les factures avec les dossiers en pause qui seraient facturés
            len_patient_invoiced_hors_pause: Nombre de patients concernés par les factures sans les dossiers en pause
            len_acts_lost: Nombre d'actes facturables mais qui ne peuvent être facturés pour une autre raison que la pause.
            len_patient_with_lost_acts: Nombre de patients concernés par des actes facturables mais qui ne peuvent être facturés pour une autre raison que la pause.
            patients_stats: Par patients, factures et actes facturables qui ne peuvent être facturés pour une autre raison que la pause.
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
                    acts_not_billable, acts_diagnostic, acts_treatment,
                    acts_losts) = self.list_for_billing()

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
                    acts_losts.keys())

                patients_stats = {}
                len_patient_with_lost_acts = 0
                len_acts_lost = 0
                for patient in patients:
                    patients_stats[patient] = {}
                    if patient in invoices.keys():
                        patients_stats[patient]['invoices'] = invoices[patient]
                        if commit and not patient.pause:
                            for invoice in invoices[patient]:
                                ppa = invoice['ppa']
                                acts = invoice['acts']
                                amount = ppa * len(acts)
                                in_o = Invoice(patient=patient,
                                    invoicing=self,
                                    ppa=invoice['ppa'],
                                    amount=amount)
                                in_o.save()
                                for act, hc in acts:
                                    act.is_billed = True
                                    act.healthcare = hc
                                    act.save()
                                    in_o.acts.add(act)
                            pass
                    if patient in acts_losts.keys():
                        # TODO: More details about healthcare
                        patients_stats[patient]['losts'] = acts_losts
                        len_patient_with_lost_acts = len_patient_with_lost_acts + 1
                        len_acts_lost = len_acts_lost + len(acts_losts[patient])
                len_patients = len(patients_stats.keys())

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
                invoices = self.invoice_set.all()
                for invoice in invoices:
                    len_invoices = len_invoices + 1
                    len_acts_invoiced = len_acts_invoiced + len(invoice.acts.all())
                    if not invoice.patient in patients_stats:
                        len_patients = len_patients + 1
                        patients_stats[invoice.patient] = {}
                        patients_stats[invoice.patient]['invoices'] = [invoice]
                    else:
                        patients_stats[invoice.patient]['invoices'].append(invoice)
                # all patients in the invoicing are invoiced
                len_patient_invoiced = 0
                # These stats are not necessary because excluded form the validated invoicing
                len_invoices_hors_pause = 0
                len_acts_invoiced_hors_pause = 0
                len_patient_invoiced_hors_pause = 0
                len_acts_lost = 0
                len_patient_with_lost_acts = 0
            return (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats, days_not_locked)
        elif 'SESSAD' in self.service.name:
            pass
        else:
            pass

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


class PricePerAct(models.Model):
    price = models.IntegerField()
    start_date = models.DateField(
            verbose_name=u"Prise d'effet",
            default=date(day=5,month=1,year=1970))
    end_date = models.DateField(
            verbose_name=u"Fin d'effet",
            blank=True,
            null=True)

    @classmethod
    def get_price(cls, at_date=None):
        if not at_date:
            at_date = date.today()
        if isinstance(at_date, datetime):
            at_date = date(day=at_date.day, month=at_date.month,
                year=at_date.year)
        found = cls.objects.filter(start_date__lte = at_date).latest('start_date')
        if not found:
            raise Exception('No price to apply')
        return found.price

    def __unicode__(self):
        val = str(self.price) + ' from ' + str(self.start_date)
        if self.end_date:
            val = val + ' to ' + str(self.end_date)
        return val


def add_price(price, start_date=None):
    price_o = None
    ppas = PricePerAct.objects.all()
    if ppas:
        if not start_date:
            raise Exception('A start date is mandatory to add a new Price')
        last_ppa = PricePerAct.objects.latest('start_date')
        if last_ppa.start_date >= start_date:
            raise Exception('The new price cannot apply before the price that currently applies.')
        if last_ppa.end_date and last_ppa.end_date != (start_date + relativedelta(days=-1)):
            raise Exception('The new price should apply the day after the last price ends.')
        last_ppa.end_date = start_date + relativedelta(days=-1)
        last_ppa.save()
    if not start_date:
        price_o = PricePerAct(price=price)
    else:
        price_o = PricePerAct(price=price, start_date=start_date)
    price_o.save()
    return price_o


# Last invoice from the previous software
INVOICE_OFFSET = 10000


class Invoice(models.Model):
    number = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(u'Création', auto_now_add=True)
    patient = models.ForeignKey('dossiers.PatientRecord')
    invoicing = models.ForeignKey('facturation.Invoicing',
        on_delete='PROTECT')
    acts = models.ManyToManyField('actes.Act')
    amount = models.IntegerField()
    ppa = models.IntegerField()

    def allocate_number(self):
        number = 1
        max_number = Invoice.objects.all() \
                .aggregate(Max('number'))['number__max']
        if max_number:
            number = number + max_number
        number = number + INVOICE_OFFSET
        return number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.allocate_number()
        super(Invoice, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Invoice n %d of %d euros for %d acts" % (self.number, self.amount, len(self.acts.all()))
