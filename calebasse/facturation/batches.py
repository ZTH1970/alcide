# -*- coding: utf-8 -*-

from collections import defaultdict

class Batch(object):
    def __init__(self, number, invoices):
        self.number = number
        self.health_center = invoices[0].health_center
        self.invoices = invoices
        self.number_of_invoices = len(invoices)
        self.total = sum(invoice.decimal_amount for invoice in invoices)
        self.number_of_acts = sum(len(invoice.acts.all()) for invoice in invoices)
        self.start_date = min(invoice.start_date for invoice in invoices)
        self.end_date = max(invoice.end_date for invoice in invoices)

    def __str__(self):
        return '%s pour %s (%d factures)' % (self.number, self.health_center, self.number_of_invoices)

def build_batches(invoicing):
    invoices = invoicing.invoice_set.order_by('number')
    prebatches = defaultdict(lambda:[])
    for invoice in invoices:
        prebatches[(invoice.health_center, invoice.batch)].append(invoice)
    batches_by_health_center = defaultdict(lambda:[])
    # FIXME / A REVOIR car il ne pas depasser 999 lignes par batches_by_health_center...
    for health_center, batch_number in sorted(prebatches.keys()):
        hc = health_center.hc_invoice or health_center
        batches_by_health_center[hc].append(Batch(batch_number,
            prebatches[(health_center, batch_number)]))
    return batches_by_health_center

