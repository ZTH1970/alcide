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

def build_batches(invoicing):
    invoices = invoicing.invoice_set.order_by('number')
    prebatches = defaultdict(lambda:[])
    for invoice in invoices:
        prebatches[invoice.batch].append(invoice)
    batches = []
    for batch_number in sorted(prebatches.keys()):
        batches.append(Batch(batch_number,
            prebatches[batch_number]))
    batches_by_health_center = defaultdict(lambda:[])
    for batch in batches:
        batches_by_health_center[batch.health_center].append(batch)
    return batches_by_health_center

