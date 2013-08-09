# -*- coding: utf-8 -*-
import os
import os.path
import tempfile
import datetime
import textwrap
from decimal import Decimal
from collections import defaultdict

from xhtml2pdf.pisa import CreatePDF
from django.template import loader, Context
from django.conf import settings

from invoice_template import InvoiceTemplate
from ..pdftk import PdfTk
from batches import build_batches
from calebasse.utils import get_nir_control_key


class Counter(object):
    def __init__(self, initial_value=0):
        self.counter = initial_value

    def increment(self):
        self.counter += 1
        return (self.counter-1)

    def __str__(self):
        return str(self.counter)


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

def price_details(service, invoicing,
                  header_service_template = 'facturation/bordereau-%s.html',
                  header_template = 'facturation/prices-details.html',
                  delete = False):
    context = {'invoicings': invoicing.get_stats_per_price_per_year()}
    return render_to_pdf_file((header_service_template % service.slug,
                               header_template),
                              context,
                              delete = delete)


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
    address = textwrap.fill(invoice.policy_holder_address, 40)
    if not invoice.first_tag:
        subtitle = 'INDEFINI'
    elif invoice.first_tag[0] == 'D':
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
    tableau1 = []
    tableau2 = []
    dates = []
    if invoice.list_dates:
        dates = invoice.list_dates.split('$')
    if dates:
        if len(dates) > 26:
            raise RuntimeError('Too much acts in invoice %s' % invoice.id)
        kind = 'X'
        offset = 0
        prestation = u'X'
        if invoice.first_tag:
            kind = invoice.first_tag[0]
            offset = int(invoice.first_tag[1:])
            prestation = u'SNS' if kind == 'T' else u'SD'
        for date in dates[:13]:
            tableau1.append([u'19', u'320', prestation, date, date,
                invoice.decimal_ppa, 1, invoice.decimal_ppa, kind + str(offset)])
            total1 += invoice.decimal_ppa
            offset += 1
        for date in dates[13:26]:
            tableau2.append([u'19', u'320', prestation, date, date,
                invoice.decimal_ppa, 1, invoice.decimal_ppa, kind + str(offset)])
            total2 += invoice.decimal_ppa
            offset += 1
    ctx.update({
            'TABLEAU1': tableau1,
            'TABLEAU2': tableau2,
        })
    ctx['SOUS_TOTAL1'] = total1
    if total2 != Decimal(0):
        ctx['SOUS_TOTAL2'] = total2
    ctx['TOTAL'] = invoice.decimal_amount

    try:
        repeat = settings.BATCH_CONTENT_TIMES_IN_INVOINCING_FILE
    except:
        repeat = 1

    output = tpl.generate(ctx)
    return [output for i in xrange(repeat)]

def render_not_cmpp_header(invoicing):
    header_template='facturation/bordereau_not_cmpp_header.html'
    management_codes = dict()
    total_acts = 0
    for invoice in invoicing.invoice_set.all():
        total_acts += invoice.acts.count()
        if invoice.policy_holder_management_code:
            management_codes.setdefault(invoice.policy_holder_management_code, []).append(invoice)
    list_management_codes = list()
    for mc, invoices in management_codes.iteritems():
        dic = dict()
        dic['code'] = mc
        dic['title'] = invoices[0].policy_holder_management_code_name
        dic['nb_files'] = len(invoices)
        nb_acts = 0
        for invoice in invoices:
            nb_acts += invoice.acts.count()
        dic['nb_acts'] = nb_acts
        list_management_codes.append(dic)
    list_management_codes.sort(key=lambda dic: dic['code'])
    ctx = {
            'now': datetime.datetime.now(),
            'service': invoicing.service,
            'start_date': invoicing.start_date,
            'end_date': invoicing.end_date,
            'list_management_codes': list_management_codes,
            'total_files': invoicing.invoice_set.count(),
            'total_acts': total_acts
    }
    prefix = '%s-invoicing-header-%s' % (
            invoicing.service.slug, invoicing.id)
    return render_to_pdf_file(
            (header_template, ), ctx, prefix=prefix, delete=True)

def render_not_cmpp_content(invoicing):
    header_template='facturation/bordereau_not_cmpp_content.html'
    total_acts = 0
    list_patients = list()
    for invoice in invoicing.invoice_set.all():
        total_acts += invoice.acts.count()
        policy_holder = ''
        if invoice.policy_holder_last_name:
            policy_holder = invoice.policy_holder_last_name.upper()
            if invoice.policy_holder_first_name:
                policy_holder += ' ' + invoice.policy_holder_first_name
        nir = None
        if invoice.policy_holder_social_security_id:
            nir = invoice.policy_holder_social_security_id + ' ' + str(get_nir_control_key(invoice.policy_holder_social_security_id))
        health_center = ''
        tp = ''
        cai = ''
        if invoice.policy_holder_healthcenter:
            health_center = invoice.policy_holder_healthcenter.name
            if invoice.policy_holder_healthcenter.large_regime:
                tp = invoice.policy_holder_healthcenter.large_regime.code
            cai = invoice.policy_holder_healthcenter.health_fund
        name = ''
        if invoice.patient_last_name:
            name = invoice.patient_last_name.upper()
            if invoice.patient_first_name:
                name += ' ' + invoice.patient_first_name
        list_patients.append({\
              'code' : invoice.policy_holder_management_code,
              'policy_holder': policy_holder,
              'nir': nir,
              'health_center': health_center,
              'tp': tp,
              'cai': cai,
              'cen': invoice.policy_holder_other_health_center,
              'number': invoice.patient_id,
              'name': name,
              'birth_date': invoice.patient_birthdate,
              'inscription_date': invoice.patient_entry_date,
              'sortie_date': invoice.patient_exit_date,
              'nb_actes': invoice.acts.count()})
    list_patients.sort(key=lambda dic: dic['policy_holder'])
    ctx = {
            'now': datetime.datetime.now(),
            'service': invoicing.service,
            'start_date': invoicing.start_date,
            'end_date': invoicing.end_date,
            'total_files': invoicing.invoice_set.count(),
            'total_acts': total_acts,
            'patients': list_patients
    }
    prefix = '%s-invoicing-content-%s' % (
            invoicing.service.slug, invoicing.id)
    return render_to_pdf_file(
            (header_template, ), ctx, prefix=prefix, delete=True)


def render_invoicing(invoicing, delete=False, headers=True, invoices=True):
    service = invoicing.service
    now = datetime.datetime.now()
    output_file = None
    all_files = [price_details(service, invoicing)]
    try:
        if service.name == 'CMPP':
            batches_by_health_center = build_batches(invoicing)
            centers = sorted(batches_by_health_center.keys())
            counter = Counter(1)
            for center in centers:
                if headers is not True and headers is not False and headers != center:
                    continue
                for batch in batches_by_health_center[center]:
                    files = batches_files(service, invoicing, center,
                        [batch], delete=delete,
                        headers=headers, invoices=invoices, counter=counter)
                    all_files.extend(files)
        else:
            header = render_not_cmpp_header(invoicing)
            all_files.append(header)
            content = render_not_cmpp_content(invoicing)
            all_files.append(content)
        output_file = None
        if settings.INVOICING_DIRECTORY and settings.INVOICING_DIRECTORY != '':
            to_path = os.path.join(settings.INVOICING_DIRECTORY, service.name)
            if not os.path.exists(to_path):
                os.makedirs(to_path)
            to_path = os.path.join(to_path, '%s-facturation-%s-%s.pdf' \
                % (service.slug, invoicing.seq_id, now.strftime('%d%m%Y-%H%M')))
            output_file = open(to_path, 'w')
        if not output_file:
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
            header = header_file(service, invoicing, health_center, batches,
                                 delete=delete, counter=counter)

            try:
                repeat = settings.BATCH_HEADER_TIMES_IN_INVOICING_FILE
            except:
                repeat = 1
            map(lambda el: files.append(header), xrange(repeat))

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
