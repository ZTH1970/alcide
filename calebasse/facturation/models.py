# -*- coding: utf-8 -*-

from datetime import date
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
                    start_date = start_date,
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
        '''Return list of acts for billing'''
        acts = None
        if self.acts.exists():
            acts = self.acts.all()
        if self.service.name == 'CMPP':
            end_date = self.end_date
            if not end_date:
                today = date.today()
                end_date = date(day=today.day, month=today.month, year=today.year)
            return list_acts.list_acts_for_billing_CMPP(end_date,
                    service=self.service, acts=acts)
        elif self.service.name == 'CAMSP':
            return list_acts.list_acts_for_billing_CAMSP(self.start_date,
                    self.end_date, service=self.service)
        elif 'SESSAD' in self.service_name:
            return list_acts.list_acts_for_billing_SESSAD(self.start_date,
                    self.end_date, service=self.service)
        else:
            raise RuntimeError('Unknown service', self.service)

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
        self.status = Invoicing.STATUS.closed
        self.end_date = end_date
        self.save()

    def validate(self):
        '''Validate a closed invoicing'''
        if self.service != 'CMPP':
            raise RuntimeError('validation is only for the CMPP')
        if self.status != Invoicing.STATUS.open:
            raise RuntimeError('closing an un-opened Invoicing')
        l = self.list_for_billing()
        acts = set()
        for d in l:
            if not isinstance(d, dict):
                continue
            for k, v in d.iteritems():
                for act in v:
                    if not isinstance(act, models.Model):
                        act = act[0]
                    acts.add(act)
        self.acts = acts
        self.status = Invoicing.STATUS.closed
        self.save()
