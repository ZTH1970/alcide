# -*- coding: utf-8 -*-

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import models
from django.db.models import Max, Q

from model_utils import Choices

from calebasse.ressources.models import ServiceLinkedManager, PricePerAct

import list_acts

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
        invoice = {}
        invoice['ppa'] = pricing.price_at_date(act.date)
        invoice['year'] = act.date.year
        invoice['acts'] = [(act, hc)]
        if len(acts) > 1:
            for act, hc in acts[1:]:
                if invoice['ppa'] != pricing.price_at_date(act.date) or \
                        invoice['year'] != act.date.year:
                    invoices[patient].append(invoice)
                    len_invoices = len_invoices + 1
                    len_acts_invoiced = len_acts_invoiced + len(invoice['acts'])
                    if not patient.pause:
                        len_invoices_hors_pause = len_invoices_hors_pause + 1
                        len_acts_invoiced_hors_pause = len_acts_invoiced_hors_pause + len(invoice['acts'])
                    invoice['ppa'] = pricing.price_at_date(act.date)
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
                    len_invoices = len_invoices + 1
                    len_acts_invoiced = len_acts_invoiced + len(invoice['acts'])
                    if not patient.pause:
                        len_invoices_hors_pause = len_invoices_hors_pause + 1
                        len_acts_invoiced_hors_pause = len_acts_invoiced_hors_pause + len(invoice['acts'])
                    invoice = dict()
                    invoice['ppa'] = pricing.price_at_date(act.date)
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
            return list_acts.list_acts_for_billing_CMPP_2(end_date,
                    service=self.service)
        elif self.service.name == 'CAMSP':
            return list_acts.list_acts_for_billing_CAMSP(self.start_date,
                    self.end_date, service=self.service)
        elif 'SESSAD' in self.service.name:
            return list_acts.list_acts_for_billing_SESSAD(self.start_date,
                    self.end_date, service=self.service)
        else:
            raise RuntimeError('Unknown service', self.service)


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
                    acts_losts_missing_policy) = \
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
                    acts_losts.keys() + acts_pause.keys() + acts_losts_missing_policy.keys())

                patients_stats = []
                len_patient_with_lost_acts = 0
                len_acts_lost = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                len_patient_with_lost_acts_missing_policy = 0
                len_acts_losts_missing_policy = 0
                for patient in patients:
                    dic = {}
                    if patient in invoices.keys():
                        dic['invoices'] = invoices[patient]
                        if commit and not patient.pause:
                            invoice_kwargs = dict(
                                    patient_id=patient.id,
                                    patient_last_name=patient.last_name,
                                    patient_first_name=patient.first_name,
                                    patient_social_security_id=patient.social_security_id,
                                    patient_birthdate=patient.birthdate,
                                    patient_twinning_rank=patient.twinning_rank,
                                    patient_healthcenter=patient.health_center,
                                    patient_other_health_center=patient.other_health_center)
                            if patient.policyholder != patient.patientcontact:
                                policy_holder = patient.policyholder
                                invoice_kwargs.update(dict(
                                    policy_holder_id=policy_holder.id,
                                    policy_holder_last_name=policy_holder.last_name,
                                    policy_holder_first_name=policy_holder.first_name,
                                    policy_holder_social_security_id=policy_holder.social_security_id,
                                    policy_holder_healthcenter=policy_holder.health_center))
                            for invoice in invoices[patient]:
                                ppa = invoice['ppa']
                                acts = invoice['acts']
                                amount = ppa * len(acts)
                                in_o = Invoice(
                                        invoicing=self,
                                        ppa=invoice['ppa'],
                                        amount=amount,
                                        **invoice_kwargs)
                                in_o.batch = Invoice.objects.new_batch_number(
                                            health_center=in_o.health_center,
                                            invoicing=self)
                                in_o.save()
                                for act, hc in acts:
                                    act.is_billed = True
                                    act.healthcare = hc
                                    act.save()
                                    in_o.acts.add(act)
                            pass
                    if patient in acts_losts.keys():
                        # TODO: More details about healthcare
                        dic['losts'] = acts_losts[patient]
                        len_patient_with_lost_acts = len_patient_with_lost_acts + 1
                        len_acts_lost = len_acts_lost + len(acts_losts[patient])
                    if patient in acts_pause.keys():
                        dic['acts_paused'] = acts_pause[patient]
                        len_patient_acts_paused = len_patient_acts_paused + 1
                        len_acts_paused = len_acts_paused + len(acts_pause[patient])
                    if patient in acts_losts_missing_policy.keys():
                        # TODO: More details about healthcare
                        dic['losts_missing_policy'] = acts_losts_missing_policy[patient]
                        len_patient_with_lost_acts_missing_policy = len_patient_with_lost_acts_missing_policy + 1
                        len_acts_losts_missing_policy = len_acts_losts_missing_policy + len(acts_losts_missing_policy[patient])
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
                for invoice in invoices:
                    len_invoices = len_invoices + 1
                    len_acts_invoiced = len_acts_invoiced + len(invoice.acts.all())
                    if not invoice.patient in patients_stats:
                        len_patients = len_patients + 1
                        patients_stats[invoice.patient] = {}
                        patients_stats[invoice.patient]['invoices'] = [invoice]
                    else:
                        patients_stats[invoice.patient]['invoices'].append(invoice)
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
            return (len_patients, len_invoices, len_invoices_hors_pause,
                len_acts_invoiced, len_acts_invoiced_hors_pause,
                len_patient_invoiced, len_patient_invoiced_hors_pause,
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused, len_acts_losts_missing_policy,
                len_patient_with_lost_acts_missing_policy)
        elif self.service.name == 'CAMSP':
            if self.status in Invoicing.STATUS.closed:
                (acts_not_locked, days_not_locked, acts_not_valide,
                acts_not_billable, acts_pause, acts_bad_state,
                acts_accepted) = self.list_for_billing()
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
                            len_patient_pause = len_patient_pause + 1
                            len_acts_pause = len_acts_pause + len(acts)
                        else:
                            len_patient_hors_pause = len_patient_hors_pause + 1
                            len_acts_hors_pause = len_acts_hors_pause + len(acts)
                            if commit:
                                for act in acts:
                                    self.acts.add(act)
                    if patient in acts_pause.keys():
                        dic['acts_paused'] = acts_pause[patient]
                        len_patient_acts_paused = len_patient_acts_paused + 1
                        len_acts_paused = len_acts_paused + len(acts_pause[patient])
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
                for act in self.acts.all():
                    if act.patient in patients_stats.keys():
                        patients_stats[act.patient]['accepted'].append(act)
                        len_acts_hors_pause = len_acts_hors_pause + 1
                    else:
                        len_patient_hors_pause = len_patient_hors_pause + 1
                        len_acts_hors_pause = len_acts_hors_pause + 1
                        patients_stats[act.patient] = {}
                        patients_stats[act.patient]['accepted'] = [act]
                patients_stats = sorted(patients_stats.items(), key=lambda patient: (patient[0].last_name, patient[0].first_name))
            return (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused)
        else:
            if self.status in Invoicing.STATUS.closed:
                (acts_not_locked, days_not_locked, acts_not_valide,
                acts_not_billable, acts_pause, acts_bad_state,
                acts_missing_valid_notification, acts_accepted) = \
                    self.list_for_billing()

                len_patient_pause = 0
                len_patient_hors_pause = 0
                len_acts_pause = 0
                len_acts_hors_pause = 0
                len_patient_acts_paused = 0
                len_acts_paused = 0
                len_patient_missing_notif = 0
                len_acts_missing_notif = 0
                patients = set(acts_accepted.keys() + acts_pause.keys())
                patients_stats = []
                for patient in patients:
                    dic = {}
                    if patient in acts_accepted.keys():
                        acts = acts_accepted[patient]
                        dic['accepted'] = acts
                        if patient.pause:
                            len_patient_pause = len_patient_pause + 1
                            len_acts_pause = len_acts_pause + len(acts)
                        else:
                            len_patient_hors_pause = len_patient_hors_pause + 1
                            len_acts_hors_pause = len_acts_hors_pause + len(acts)
                            if commit:
                                for act in acts:
                                    self.acts.add(act)
                    if patient in acts_missing_valid_notification.keys():
                        acts = acts_missing_valid_notification[patient]
                        dic['missings'] = acts
                        len_patient_missing_notif = len_patient_missing_notif + 1
                        len_acts_missing_notif = len_acts_missing_notif + len(acts)
                        if not 'accepted' in dic:
                            len_patient_hors_pause = len_patient_hors_pause + 1
                        if commit:
                            for act in acts:
                                self.acts.add(act)
                    if patient in acts_pause.keys():
                        dic['acts_paused'] = acts_pause[patient]
                        len_patient_acts_paused = len_patient_acts_paused + 1
                        len_acts_paused = len_acts_paused + len(acts_pause[patient])
                    patients_stats.append((patient, dic))
                patients_stats = sorted(patients_stats, key=lambda patient: (patient[0].last_name, patient[0].first_name))
                len_acts_hors_pause = len_acts_hors_pause + len_acts_missing_notif
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
                for act in self.acts.all():
                    if act.patient in patients_stats.keys():
                        patients_stats[act.patient]['accepted'].append(act)
                        len_acts_hors_pause = len_acts_hors_pause + 1
                    else:
                        len_patient_hors_pause = len_patient_hors_pause + 1
                        len_acts_hors_pause = len_acts_hors_pause + 1
                        patients_stats[act.patient] = {}
                        patients_stats[act.patient]['accepted'] = [act]
                patients_stats = sorted(patients_stats.items(), key=lambda patient: (patient[0].last_name, patient[0].first_name))
            return (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause,
                len_patient_missing_notif, len_acts_missing_notif,
                patients_stats, days_not_locked,
                len_patient_acts_paused, len_acts_paused)

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
    'SM00000091007381': 98,
    'SM00000092001422': 14,
    'SM00000092001691': 13,
    'SM00000099038939': 24,
}


class InvoiceManager(models.Manager):
    def new_batch_number(self, health_center, invoicing):
        '''Compute the next batch number for the given health center'''
        global PREVIOUS_MAX_BATCH_NUMBERS
        agg = self \
                .filter(invoicing__seq_id__lt=invoicing.seq_id) \
                .filter(
                    Q(patient_healthcenter=health_center,
                        policy_holder_healthcenter__isnull=True)|
                    Q(policy_holder_healthcenter=health_center)) \
                        .aggregate(Max('batch'))
        max_bn = agg['batch__max']
        if max_bn is None:
            max_bn = PREVIOUS_MAX_BATCH_NUMBERS.get(health_center.b2_000(), 0)
        return max_bn + 1


class Invoice(models.Model):
    number = models.IntegerField(blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)
    # the patient can be modified (or even deleted) after invoice creation, so
    # we copy his informations here
    patient_id = models.IntegerField(blank=True, null=True)
    patient_last_name = models.CharField(max_length=128,
            verbose_name=u'Nom du patient')
    patient_first_name = models.CharField(max_length=128,
            verbose_name=u'Prénom(s) du patient', blank=True, null=True)
    patient_social_security_id = models.CharField(max_length=13,
            verbose_name=u"NIR", null=True, blank=True)
    patient_birthdate = models.DateField(verbose_name=u"Date de naissance",
            null=True, blank=True)
    patient_twinning_rank = models.IntegerField(
        verbose_name=u"Rang (gémellité)",
        null=True, blank=True)
    patient_healthcenter = models.ForeignKey('ressources.HealthCenter',
            verbose_name=u"Centre d'assurance maladie",
            related_name='related_by_patient_invoices',
            null=True, blank=True)
    patient_other_health_center = models.CharField(
        verbose_name=u"Centre spécifique", max_length=4, null=True, blank=True)
    # policy holder informations
    policy_holder_id = models.IntegerField(blank=True, null=True)
    policy_holder_last_name = models.CharField(max_length=128,
            verbose_name=u'Nom de l\'assuré', blank=True)
    policy_holder_first_name = models.CharField(max_length=128,
            verbose_name=u'Prénom(s) de l\' assuré', blank=True)
    policy_holder_social_security_id = models.CharField(max_length=13,
            verbose_name=u"NIR de l\'assuré", blank=True)
    policy_holder_healthcenter = models.ForeignKey('ressources.HealthCenter',
            verbose_name=u"Centre d'assurance maladie de l\'assuré",
            related_name='related_by_policy_holder_invoices',
            null=True, blank=True)
    created = models.DateTimeField(u'Création', auto_now_add=True)
    invoicing = models.ForeignKey('facturation.Invoicing',
        on_delete='PROTECT')
    acts = models.ManyToManyField('actes.Act')
    amount = models.IntegerField()
    ppa = models.IntegerField()

    def save(self, *args, **kwargs):
        invoicing = self.invoicing
        self.number = invoicing.seq_id * 100000 + 1
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
        return Decimal(self.amout) / Decimal(100)

    def __unicode__(self):
        return "Facture %d de %d euros (%d actes)" % (self.number, self.amount, len(self.acts.all()))
