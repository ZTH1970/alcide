# -*- coding: utf-8 -*-

import os
import sys
import re
import glob
import tempfile
import time
import datetime
import hashlib
import base64
import json
from smtplib import SMTP, SMTPException

from calebasse.facturation.models import Invoicing
from batches import build_batches
from transmission_utils import build_mail

DEFAULT_OUTPUT_DIRECTORY = '/var/lib/calebasse/B2'
DEFAULT_NORME = 'CP  '
DEFAULT_TYPE_EMETTEUR = 'TE'
DEFAULT_APPLICATION = 'TR'
DEFAULT_CATEGORIE = '189'
DEFAULT_STATUT = '60'
DEFAULT_MODE_TARIF = '05'
DEFAULT_MESSAGE = 'ENTROUVERT 0143350135 CALEBASSE 1307'

# B2 informations / configuration
# from settings.py :
# B2_TRANSMISSION = {
#     'nom': 'CMPP FOOBAR',
#     'numero_emetteur': '123456789',
#     'smtp_from': 'transmission@domaine.fr',
#     ...
# }

try:
    from django.conf import settings
    b2_transmission_settings = settings.B2_TRANSMISSION or {}
except (ImportError, AttributeError):
    b2_transmission_settings = {}

# B2 informations
NORME = b2_transmission_settings.get('norme', DEFAULT_NORME)

TYPE_EMETTEUR = b2_transmission_settings.get('type_emetteur', DEFAULT_TYPE_EMETTEUR)
NUMERO_EMETTEUR = b2_transmission_settings.get('numero_emetteur')
APPLICATION = b2_transmission_settings.get('application', DEFAULT_APPLICATION)

CATEGORIE = b2_transmission_settings.get('categorie', DEFAULT_CATEGORIE)
STATUT = b2_transmission_settings.get('statut', DEFAULT_STATUT)
MODE_TARIF = b2_transmission_settings.get('mode_tarif', DEFAULT_MODE_TARIF)

NOM = b2_transmission_settings.get('nom', '')[:40]
NOM = NOM + ' '*(40-len(NOM))

MESSAGE = b2_transmission_settings.get('message', DEFAULT_MESSAGE)[:37]
MESSAGE = MESSAGE + ' '*(37-len(MESSAGE))

# b2 output
OUTPUT_DIRECTORY = b2_transmission_settings.get('output_directory', DEFAULT_OUTPUT_DIRECTORY)

# mailing
SMTP_FROM = b2_transmission_settings.get('smtp_from')
SMTP_HOST = b2_transmission_settings.get('smtp_host', '127.0.0.1')
SMTP_PORT = b2_transmission_settings.get('smtp_port', 25)
SMTP_LOGIN = b2_transmission_settings.get('smtp_login')
SMTP_PASSWORD = b2_transmission_settings.get('smtp_password')
SMTP_DELAY = b2_transmission_settings.get('smtp_delay')

# if "smtp_debug_to" setting is present, send all B2 mails to this address
# instead of real ones (yy.xxx@xxx.yy.rss.fr) and output SMTP dialog
DEBUG_TO = b2_transmission_settings.get('smtp_debug_to')


def b2_is_configured():
    if 'nom' in b2_transmission_settings and \
            'numero_emetteur' in b2_transmission_settings and \
            'smtp_from' in b2_transmission_settings:
        return True
    return False

def b2_output_directory():
    if not os.path.isdir(OUTPUT_DIRECTORY):
        raise IOError('B2 output directory (%s) is not a directory' % OUTPUT_DIRECTORY)
    if not os.access(OUTPUT_DIRECTORY, os.R_OK + os.W_OK + os.X_OK):
        raise IOError('B2 output directory (%s) is not accessible (rwx)' % OUTPUT_DIRECTORY)
    return OUTPUT_DIRECTORY

def filler(n, car=' '):
    return car*n
def filler0(n):
    return filler(n, '0')
def b2date(d):
    return d.strftime('%y%m%d')
def get_control_key(nir):
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
        return '%0.2d' % (97 - (nir % 97))
    except Exception, e:
        return '00'


def write128(output_file, line):
    if len(line) != 128:
        raise RuntimeError('length of this B2 line is %d != 128 : "%s"' %
                (len(line), line))
    output_file.write(line)

def write_invoice(output_file, invoice):
    invoice_lines = 0
    start_date = invoice.start_date
    start_2 = '2' + NUMERO_EMETTEUR + ' ' + \
            invoice.policy_holder_social_security_id + \
            get_control_key(invoice.policy_holder_social_security_id) + \
            '000' + ('%0.9d' % invoice.number) + \
            '1' + ('%0.9d' % invoice.patient_id) + \
            invoice.policy_holder_healthcenter.large_regime.code + \
            invoice.policy_holder_healthcenter.dest_organism + \
            (invoice.policy_holder_other_health_center or '0000') + \
            '3' + b2date(start_date) + '000000' + \
            invoice.policy_holder_healthcenter.dest_organism + '000' + \
            '10' + '3' +  \
            b2date(start_date) + \
            '000000000' + ' ' + \
            b2date(invoice.patient_birthdate) + \
            ('%d' %  invoice.patient_twinning_rank)[-1:] + \
            b2date(start_date) + b2date(invoice.end_date) + '01' + \
            '00' + filler(10)
    write128(output_file, start_2)
    invoice_lines += 1
    nb_type3 = 0
    kind = invoice.first_tag[0]
    prestation = u'SNS  ' if kind == 'T' else u'SD   '
    for date in invoice.list_dates.split('$'):
        line_3 = '3' + NUMERO_EMETTEUR + ' ' + \
                invoice.policy_holder_social_security_id + \
                get_control_key(invoice.policy_holder_social_security_id) + \
                '000' + ('%0.9d' % invoice.number) + \
                '19' + '320' + \
                b2date(datetime.datetime.strptime(date, "%d/%m/%Y")) + \
                b2date(datetime.datetime.strptime(date, "%d/%m/%Y")) + \
                prestation + '001' + \
                ' ' + '00100' +  ' ' + '00000' + \
                ('%0.7d' % invoice.ppa) + \
                ('%0.8d' % invoice.ppa) + \
                '100' + \
                ('%0.8d' % invoice.ppa) + \
                ('%0.8d' % invoice.ppa) + \
                '0000' + '000' + ' ' + filler(2) + ' ' + \
                ' ' + '0000000'
        write128(output_file, line_3)
        invoice_lines += 1
        nb_type3 += 1

    end_5 = '5' + NUMERO_EMETTEUR + ' ' + \
            invoice.policy_holder_social_security_id + \
            get_control_key(invoice.policy_holder_social_security_id) + \
            '000' + ('%0.9d' % invoice.number) + \
            ('%0.3d' % nb_type3) + \
            ('%0.8d' % invoice.amount) + \
            ('%0.8d' % invoice.amount) + \
            '00000000' + '00000000' + '00000000' + '00000000' + '00000000' + \
            filler(17) + \
            ('%0.8d' % invoice.amount) + \
            filler(4+2)
    write128(output_file, end_5)
    invoice_lines += 1

    return invoice_lines

def b2(seq_id, hc, batches):
    to = hc.b2_000()
    total = sum(b.total for b in batches)
    first_batch = min(b.number for b in batches)

    output_dir = os.path.join(b2_output_directory(), '%s' % seq_id)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    infos = {
            'seq_id': seq_id,
            'hc': u'%s' % hc,
            'hc_b2': to,
            'batches': [],
            'total': float(total)
            }

    # B2 veut un identifiant de fichier sur 6 caractères alphanum
    hexdigest = hashlib.sha256('%s%s%s%s%s' % (seq_id, first_batch, NUMERO_EMETTEUR, to, total)).hexdigest()
    file_id = base64.encodestring(hexdigest).upper()[0:6]
    prefix = '%s-%s-%s-%s-%s.' % (seq_id, NUMERO_EMETTEUR, to, first_batch, file_id)

    b2_filename = os.path.join(output_dir, prefix + 'b2')
    assert not os.path.isfile(b2_filename), 'B2 file "%s" already exists' % b2_filename

    output_file = tempfile.NamedTemporaryFile(suffix='.b2tmp',
            prefix=prefix, dir=output_dir, delete=False)

    nb_lines = 0

    utcnow = datetime.datetime.utcnow()
    start_000 = '000' +  TYPE_EMETTEUR + '00000' + NUMERO_EMETTEUR + \
            filler(6) + to + filler(6) + APPLICATION + \
            file_id + b2date(utcnow) + NORME + 'B2' + filler(15) + \
            '128' + filler(6) + MESSAGE
    write128(output_file, start_000)
    nb_lines += 1
    nb_batches = 0

    for batch in batches:
        start_1 = '1' + NUMERO_EMETTEUR + filler(6) + \
                batch.health_center.dest_organism[0:3] + \
                ('%0.3d' % batch.number) + CATEGORIE + STATUT + MODE_TARIF + \
                NOM + 'B2' + b2date(utcnow) + ' ' + NORME[0:2] + \
                ' ' + '062007' + 'U' + filler(2+3+1+34)
        write128(output_file, start_1)
        nb_lines += 1

        infos['batches'].append({
            'batch': batch.number,
            'hc': u'%s' % batch.health_center,
            'total': float(batch.total),
            'number_of_invoices': batch.number_of_invoices,
            'number_of_acts': batch.number_of_acts
            })

        for i in batch.invoices:
            nb_lines += write_invoice(output_file, i)

        end_6 = '6' + NUMERO_EMETTEUR + \
                ('%0.3d' % batch.number_of_invoices) + \
                ('%0.4d' % batch.number_of_acts) + \
                ('%0.4d' % batch.number_of_invoices) + \
                ('%0.3d' % batch.number_of_invoices) + \
                ('%0.9d' % (batch.total * 100)) + \
                ('%0.9d' % (batch.total * 100)) + \
                '000000000' + ('%0.3d' % batch.number) + \
                filler(1+1+4+12+12+3+9+32)
        write128(output_file, end_6)
        nb_lines += 1
        nb_batches += 1

    if nb_lines > 990:
        raise

    end_999 = '999' +  TYPE_EMETTEUR + '00000' + NUMERO_EMETTEUR + \
            filler(6) + to + filler(6) + APPLICATION + \
            file_id + \
            ('%0.8d' % (nb_lines+1)) + \
            filler(19) + \
            ('%0.3d' % nb_batches) + \
            filler(43)
    write128(output_file, end_999)

    old_filename = output_file.name
    output_file.close()

    b2_filename = os.path.join(output_dir, prefix + 'b2')
    os.rename(old_filename, b2_filename)

    # create S/MIME mail
    fd = open(b2_filename + '-mail', 'w')
    fd.write(build_mail(hc.large_regime.code, hc.dest_organism, b2_filename))
    fd.close()

    # create info file (json)
    basename = os.path.basename(b2_filename)
    infos['files'] = {
            'b2': basename,
            'self': basename + '-info',
            'mail': basename + '-mail'
            }
    fd = open(b2_filename + '-info', 'w')
    json.dump(infos, fd, sort_keys=True, indent=4, separators=(',', ': '))
    fd.close()

    return b2_filename

def buildall(seq_id):
    try:
        invoicing = Invoicing.objects.filter(seq_id=seq_id)[0]
    except IndexError:
        raise RuntimeError('Facture introuvable')
    batches = build_batches(invoicing)
    for hc in batches:
        for b in batches[hc]:
            b2_filename = b2(invoicing.seq_id, hc, [b])


def sendmail_raw(mail):
    if DEBUG_TO:
        toaddr = DEBUG_TO
        print '(debug mode, sending to', toaddr, ')'
    else:
        toaddr = re.search('\nTo: +(.*)\n', mail, re.MULTILINE).group(1)

    smtp = SMTP(SMTP_HOST, SMTP_PORT)
    if DEBUG_TO:
        smtp.set_debuglevel(1)
    smtp.ehlo()
    if SMTP_LOGIN and SMTP_PASSWORD:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(SMTP_LOGIN, SMTP_PASSWORD)
    smtp.sendmail(SMTP_FROM, toaddr, mail)
    smtp.close()
    return toaddr, "%s:%s" % (SMTP_HOST, SMTP_PORT)

def sendmail(seq_id, oneb2=None):
    output_dir = os.path.join(b2_output_directory(), '%s' % seq_id)
    if oneb2:
        filename = os.path.join(output_dir, oneb2 + '-mail')
        if os.path.isfile(filename + '-sent'): # resent
            os.rename(filename + '-sent', filename)
        filenames = [filename]
    else:
        filenames = glob.glob(os.path.join(output_dir, '*.b2-mail'))
    for mail_filename in filenames:
        log = open(mail_filename + '.log', 'a')
        log.write('%s mail %s\n' % (datetime.datetime.now(), os.path.basename(mail_filename)))
        mail = open(mail_filename).read()
        try:
            to, via = sendmail_raw(mail)
        except SMTPException as e:
            log.write('%s SMTP ERROR: %s\n' % (datetime.datetime.now(), e))
        else:
            log.write('%s OK, MAIL SENT TO %s VIA %s\n' % (datetime.datetime.now(), to, via))
            os.rename(mail_filename, mail_filename + '-sent')
            os.utime(mail_filename + '-sent', None) # touch
        log.close()
        if SMTP_DELAY:
            time.sleep(SMTP_DELAY) # Exchange, I love you.


def get_all_infos(seq_id):
    output_dir = os.path.join(b2_output_directory(), '%s' % seq_id)
    infos = []
    for mail_filename in glob.glob(os.path.join(output_dir, '*.b2-info')):
        fd = open(mail_filename, 'r')
        info = json.load(fd)
        stats = os.stat(os.path.join(output_dir, info['files']['b2']))
        info['creation_date'] = datetime.datetime.fromtimestamp(stats.st_mtime)
        try:
            stats = os.stat(os.path.join(output_dir, info['files']['mail'] + '-sent'))
            info['mail_date'] = datetime.datetime.fromtimestamp(stats.st_mtime)
        except:
            pass
        try:
            fd = open(os.path.join(output_dir, info['files']['mail'] + '.log'), 'r')
            info['mail_log'] = fd.read()
            fd.close()
        except:
            pass
        infos.append(info)
        fd.close()
    return infos
