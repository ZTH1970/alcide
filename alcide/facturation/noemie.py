import os
from datetime import datetime
import time
import email
from glob import glob
from gzip import GzipFile
from StringIO import StringIO

from noemie_format import NOEMIE
from b2 import b2_transmission_settings

DEFAULT_NOEMIE_DIRECTORY = '/var/lib/alcide/B2/NOEMIE'

NOEMIE_DIRECTORY = b2_transmission_settings.get('noemie_directory', DEFAULT_NOEMIE_DIRECTORY)

def noemie_output_directory():
    if not os.path.isdir(NOEMIE_DIRECTORY):
        raise IOError('NOEMIE output directory (%s) is not a directory' % NOEMIE_DIRECTORY)
    if not os.access(NOEMIE_DIRECTORY, os.R_OK + os.X_OK):
        raise IOError('NOEMIE output directory (%s) is not readable (r-x)' % NOEMIE_DIRECTORY)
    return NOEMIE_DIRECTORY


def noemie_try_gunzip(data):
    "gunzip data if it is a gzip stream"
    sio = StringIO(data)
    gz = GzipFile(fileobj=sio, mode='rb')
    try:
        data = gz.read()
    except IOError:
        pass
    return data

def noemie_decode(data):
    lines = []
    entity = ''
    while data and entity != '999':
        entity = data[:3]
        analyzer = NOEMIE.get(entity)
        if analyzer is None:
            split = data.split('@',1)
            if len(split) < 2:
                raw, data = data, ''
            else:
                raw, data = split
            lines.append({
                'description': 'Error: unknown entity %s' % entity,
                'segments': [],
                'raw': raw,
            })
            continue
        line = { 'description': analyzer['description'] }
        segments = []
        index = 0
        for anaseg in analyzer.get('segments',[]):
            seg = {
                'name': anaseg['name'],
                }
            value = data[index : index+anaseg['size']]
            if anaseg.get('values'):
                seg['raw'] = value
                value = anaseg['values'].get(value)
            seg['value'] = value
            index += anaseg['size']
            segments.append(seg)
        line['segments'] = segments
        line['raw'] = data[:index]
        data = data[index:]
        lines.append(line)
    return lines


def noemie_from_mail(name, with_data=True):
    filename = os.path.join(noemie_output_directory(), name)
    fp = open(filename, 'rb')
    try:
        mail = email.message_from_file(fp)
    except:
        fp.close()
        return None
    fp.close()

    noemie = [part for part in mail.walk() \
        if part.get_content_type().lower() == 'application/edi-consent']
    if not noemie:
        return None
    noemie = noemie[0] # only one NOEMIE part per email

    subject = mail.get('Subject')
    from_addr = mail.get('From')
    to_addr = mail.get('To')
    nature = noemie.get('Content-Description')
    if with_data:
        data = noemie.get_payload()
        if 'base64' == noemie.get('Content-Transfer-Encoding').lower():
            data = data.decode('base64')
        data = noemie_try_gunzip(data)
        data = noemie_decode(data)

    filedate = datetime.fromtimestamp(os.stat(filename).st_mtime)
    try:
        date = email.Utils.parsedate(mail.get('Date', mail.get('Delivery-date')))
        if isinstance(date, tuple):
            date = datetime.fromtimestamp(time.mktime(date))
        else:
            date = filedate
    except:
        date = filedate

    # TODO: try to get HealthCenter from from_addr
    result = {
            'name': name,
            'date': date,
            'from': from_addr,
            'to': to_addr,
            'subject': subject,
            'nature': nature,
            }
    if with_data:
        result['data'] = data
    return result

def noemie_mails():
    mails = []
    for filename in glob(os.path.join(noemie_output_directory(), '*')):
        mail = noemie_from_mail(os.path.basename(filename), with_data=False)
        if mail:
            mails.append(mail)
    mails.sort(key=lambda x: x['date'], reverse=True)
    return mails
