# -*- coding: utf-8 -*-
import os
import os.path
import tempfile
import datetime
from decimal import Decimal
from collections import defaultdict

from xhtml2pdf.pisa import CreatePDF
from django.template import loader, Context

from invoice_template import InvoiceTemplate
from ..pdftk import PdfTk

class Counter(object):
    def __init__(self, initial_value=0):
        self.counter = initial_value

    def increment(self):
        self.counter += 1
        return (self.counter-1)

    def __str__(self):
        return str(self.counter)


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


def render_to_pdf_file(templates, ctx, prefix='tmp', delete=False):
    temp = tempfile.NamedTemporaryFile(prefix=prefix, suffix='.pdf',
            delete=False)
    try:
        t = loader.select_template(templates)
        html = t.render(Context(ctx))
        CreatePDF(html, temp)
        temp.flush()
        return temp.name
    except:
        if delete:
            try:
                os.unlink(temp.name)
            except:
                pass
        raise


def header_file(service, invoicing, health_center, batches,
        header_service_template='facturation/bordereau-%s.html',
        header_template='facturation/bordereau.html',
        delete=False,
        counter=None):
    synthesis = {
            'total': sum(batch.total for batch in batches),
            'number_of_acts': sum(batch.number_of_acts for batch in batches),
            'number_of_invoices': sum(batch.number_of_invoices for batch in batches),
    }
    ctx = {
            'now': datetime.datetime.now(),
            'health_center': health_center,
            'service': service,
            'batches': batches,
            'synthesis': synthesis,
            'counter': counter,
    }
    prefix = '%s-invoicing-%s-healthcenter-%s-' % (
            service.slug, invoicing.id, health_center.id)
    return render_to_pdf_file(
            (header_service_template % service.slug,
            header_template), ctx, prefix=prefix, delete=delete)


def invoice_files(service, invoicing, batch, invoice, counter=None):
    template_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'facturation',
            'invoice.pdf')
    tpl = InvoiceTemplate(
            template_path=template_path,
            prefix='%s-invoicing-%s-invoice-%s-'
                % ( service.slug, invoicing.id, invoice.id),
            suffix='-%s.pdf' % datetime.datetime.now())
    health_center = invoice.health_center
    code_organisme = u'%s - %s %s' % (
      health_center.large_regime.code,
      health_center.dest_organism,
      health_center.name)
    address = invoice.policy_holder_address
    address = address[:40] + '\n' + address[40:80] + '\n' + address[80:120]
    if invoice.acts.all()[0].get_hc_tag()[0] == 'D':
        subtitle = 'DIAGNOSTIC'
    else:
        subtitle = 'TRAITEMENT'
    ctx = {
            'NUM_FINESS': '420788606',
            'NUM_LOT': unicode(batch.number),
            'NUM_FACTURE': unicode(invoice.number),
            'NUM_ENTREE': unicode(invoice.patient_id),
            'IDENTIFICATION_ETABLISSEMENT': '''%s SAINT ETIENNE
66/68, RUE MARENGO
42000 SAINT ETIENNE''' % service.name,
            'DATE_ELABORATION': datetime.datetime.now().strftime('%d/%m/%Y'),
            'NOM_BENEFICIAIRE': u' '.join((invoice.patient_first_name,
                invoice.patient_last_name.upper())),
            'NIR_BENEFICIAIRE': invoice.patient_social_security_id_full,
            'DATE_NAISSANCE_RANG': u' '.join(
                (unicode(invoice.patient_birthdate),
                    unicode(invoice.patient_twinning_rank))),
            'CODE_ORGANISME':  code_organisme,
            'ABSENCE_SIGNATURE': True,
            'ADRESSE_ASSURE': address,
            'SUBTITLE': subtitle,
            'PART_OBLIGATOIRE': True,
            'PART_COMPLEMENTAIRE': True,
    }
    if counter is not None:
        ctx['COUNTER'] = counter.increment()
    if invoice.patient_entry_date is not None:
        ctx['DATE_ENTREE'] = invoice.patient_entry_date.strftime('%d/%m/%Y')
    if invoice.patient_exit_date is not None:
        ctx['DATE_SORTIE'] = invoice.patient_exit_date.strftime('%d/%m/%Y')
    if invoice.policy_holder_id != invoice.patient_id:
        ctx.update({
                'NOM_ASSURE': u' '.join((
                    invoice.policy_holder_first_name,
                    invoice.policy_holder_last_name.upper())),
                'NIR_ASSURE': invoice.policy_holder_social_security_id_full,
            })
    total1 = Decimal(0)
    total2 = Decimal(0)
    acts = invoice.acts.order_by('date')
    if len(acts) > 24:
        raise RuntimeError('Too much acts in invoice %s' % invoice.id)
    tableau1 = []
    tableau2 = []
    for act in acts[:12]:
        hc_tag = act.get_hc_tag()
        prestation = u'SNS' if hc_tag.startswith('T') else u'SD'
        d = act.date.strftime('%d/%m/%Y')
        total1 += invoice.decimal_ppa
        tableau1.append([u'19', u'320', prestation, d, d, invoice.decimal_ppa,
            1, invoice.decimal_ppa, act.get_hc_tag()])
    for act in acts[12:24]:
        hc_tag = act.get_hc_tag()
        prestation = u'SNS' if hc_tag.startswith('T') else u'SD'
        d = act.date.strftime('%d/%m/%Y')
        total2 += invoice.decimal_ppa
        tableau2.append([u'19', u'320', prestation, d, d, invoice.decimal_ppa,
            1, invoice.decimal_ppa, act.get_hc_tag()])
    ctx.update({
            'TABLEAU1': tableau1,
            'TABLEAU2': tableau2,
        })
    ctx['SOUS_TOTAL1'] = total1
    if total2 != Decimal(0):
        ctx['SOUS_TOTAL2'] = total2
    assert invoice.decimal_amount == (total1+total2), "decimal_amount(%s) != " \
        "total1+total2(%s), ppa: %s len(acts): %s" % (invoice.decimal_amount,
    total1+total2, invoice.ppa, len(acts))
    ctx['TOTAL'] = total1+total2
    return [tpl.generate(ctx)]


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


def render_invoicing(invoicing, delete=False, headers=True, invoices=True):
    service = invoicing.service
    now = datetime.datetime.now()
    batches_by_health_center = build_batches(invoicing)
    centers = sorted(batches_by_health_center.keys())
    all_files = []
    output_file = None
    counter = Counter(1)
    try:
        for center in centers:
            if headers is not True and headers is not False and headers != center:
                continue
            files = batches_files(service, invoicing, center,
                batches_by_health_center[center], delete=delete,
                headers=headers, invoices=invoices, counter=counter)
            all_files.extend(files)
        output_file = tempfile.NamedTemporaryFile(prefix='%s-invoicing-%s-' %
                (service.slug, invoicing.id), suffix='-%s.pdf' % now, delete=False)
        pdftk = PdfTk()
        pdftk.concat(all_files, output_file.name)
        return output_file.name
    except:
        if delete and output_file:
            try:
                os.unlink(output_file.name)
            except:
                pass
        raise
    finally:
        # eventual cleanup
        if delete:
            for path in all_files:
                try:
                    os.unlink(path)
                except:
                    pass



def batches_files(service, invoicing, health_center, batches, delete=False,
        headers=True, invoices=True, counter=None):
    files = []
    try:
        if headers:
            files.append(header_file(service, invoicing, health_center,
                batches, delete=delete, counter=counter))

        if invoices:
            for batch in batches:
                for invoice in batch.invoices:
                    # if invoices is a sequence, skip unlisted invoices
                    if invoices is not True and invoice not in invoices:
                        continue
                    files.extend(invoice_files(service, invoicing, batch, invoice, counter=counter))
        return files
    except:
        # cleanup
        if delete:
            for path in files:
                try:
                    os.unlink(path)
                except:
                    pass
        raise
