# -*- coding: utf-8 -*-
import os.path
import tempfile
import datetime
from decimal import Decimal
from collections import defaultdict

from xhtml2pdf.pisa import CreatePDF
from django.template.loader import render_to_string

from invoice_template import InvoiceTemplate
from ..pdftk import PdfTk

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

def render_to_pdf_file(template, ctx):
    temp = tempfile.NamedTemporaryFile(delete=False)
    html = render_to_string(template, ctx)
    CreatePDF(html, temp)
    temp.flush()
    return temp.name

def header_file(service, batches,
        header_template='facturation/bordereau.html'):
    synthesis = {
            'total': sum(batch.total for batch in batches),
            'number_of_acts': sum(batch.number_of_acts for batch in batches),
            'number_of_invoices': sum(batch.number_of_invoices for batch in batches),
    }
    ctx = {
            'service': service,
            'batches': batches,
            'synthesis': synthesis,
    }
    return render_to_pdf_file(header_template, ctx)

def invoice_files(service, batch, invoice):
    template_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'facturation',
            'invoice.pdf')
    tpl = InvoiceTemplate(template_path=template_path)
    tpl.feed(InvoiceTemplate.NUM_FINESS, '420788606')
    tpl.feed(InvoiceTemplate.IDENTIFICATION_ETABLISSEMENT,
            '''%s SAINT ETIENNE
66/68, RUE MARENGO
42000 SAINT ETIENNE''' % service.name)
    tpl.feed(InvoiceTemplate.NUM_LOT, unicode(batch.number))
    tpl.feed(InvoiceTemplate.NUM_FACTURE, unicode(invoice.number))
    tpl.feed(InvoiceTemplate.NUM_ENTREE, unicode(invoice.patient_id))
    tpl.feed(InvoiceTemplate.DATE_ELABORATION, 
            datetime.datetime.now().strftime('%d/%m/%Y'))
    tpl.feed(InvoiceTemplate.NOM_BENEFICIAIRE,
            u' '.join((invoice.patient_first_name,
                invoice.patient_last_name)))
    tpl.feed(InvoiceTemplate.DATE_NAISSANCE_RANG,
            u' '.join((unicode(invoice.patient_birthdate),
                unicode(invoice.patient_twinning_rank))))
    tpl.feed(InvoiceTemplate.IMMAT_CLE, invoice.patient_social_security_id)
    # FIXME le nir de qui du patient ou de l'assuré ?
    #tpl.feed(InvoiceTemplate.IMMAT_CLE, )
    # FIXME quel healthcenter ?
    # healthcenter = None
    # code_organisme = '%s - %s %s' % (
    #   health_center.large_regime.code,
    #   health_center.dest_organism,
    #   health_center.name)
    # tpl.feed(InvoiceTemplate.CODE_ORGANISME, code_organisme)
    tpl.feed(InvoiceTemplate.DATE_ENTREE, invoice.start_date.strftime('%d/%m/%Y'))
    tpl.feed(InvoiceTemplate.DATE_SORTIE, invoice.end_date.strftime('%d/%m/%Y'))
    tpl.feed(InvoiceTemplate.ABSENCE_SIGNATURE, True)
    if invoice.policy_holder_id:
        tpl.feed(InvoiceTemplate.NOM_ASSURE, u' '.join((
            invoice.policy_holder_first_name,
            invoice.policy_holder_last_name)))
        tpl.feed(InvoiceTemplate.IMMAT_CLE,
            invoice.policy_holder_social_security_id)
        tpl.feed(InvoiceTemplate.ADRESSE1, invoice.policy_holder_address[:47])
        tpl.feed(InvoiceTemplate.ADRESSE2,
                invoice.policy_holder_address[47:47+104])
    total1 = Decimal(0)
    total2 = Decimal(0)
    acts = invoice.acts.order_by('date')
    if len(acts) > 24:
        raise RuntimeError('Too much acts in invoice %s' % invoice.id)
    for act in acts[:12]:
        hc_tag = act.get_hc_tag()
        prestation = u'SNS' if hc_tag.startswith('T') else u'SD'
        d = act.date.strftime('%d/%m/%Y')
        total1 += invoice.decimal_ppa
        tpl.feed_line(u'19', u'320', prestation, d, d, invoice.decimal_ppa, 1, invoice.decimal_ppa)
    for act in acts[12:24]:
        hc_tag = act.get_hc_tag()
        prestation = u'SNS' if hc_tag.startswith('T') else u'SD'
        d = act.date.strftime('%d/%m/%Y')
        total2 += invoice.decimal_ppa
        tpl.feed_line(u'19', u'320', prestation, d, d, invoice.decimal_ppa, 1, invoice.decimal_ppa)
    tpl.feed(InvoiceTemplate.SOUSTOTAL1, total1)
    if total2 != Decimal(0):
        tpl.feed(InvoiceTemplate.SOUSTOTAL2, total2)
    assert invoice.decimal_amount == (total1+total2), "decimal_amount(%s) != total1+total2(%s), ppa: %s len(acts): %s" % (invoice.decimal_amount, total1+total2, invoice.ppa, len(acts))
    tpl.feed(InvoiceTemplate.TOTAL2, total1+total2)
    return [tpl.generate()]

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

def render_invoicing(service, invoicing):
    batches_by_health_center = build_batches(invoicing)
    centers = sorted(batches_by_health_center.keys())
    files = []
    for center in centers:
        files.extend(batches_files(service, batches_by_health_center[center]))
    output_file = tempfile.NamedTemporaryFile(delete=False)
    pdftk = PdfTk()
    pdftk.concat(files, output_file.name)
    return output_file.name


def batches_files(service, batches):
    files = []
    files.append(header_file(service, batches))
    for batch in batches:
        for invoice in batch.invoices:
            files.extend(invoice_files(service, batch, invoice))
    return files


if __name__ == '__main__':
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calebasse.settings")
