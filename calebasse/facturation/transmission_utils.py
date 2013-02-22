# -*- coding: utf-8 -*-

import os
import sys
import re
import base64
from datetime import datetime
import zlib

import ldap
from M2Crypto import X509, SSL, Rand, SMIME, BIO

MODE_TEST = False
MODE_COMPRESS = True

LDAP_HOST = 'ldap://annuaire.gip-cps.fr'

if MODE_TEST:
    LDAP_BASEDN = 'o=gip-cps-test,c=fr'
    CAPATH = '/var/lib/calebasse/test-gip-cps.capath/'
else:
    # production
    LDAP_BASEDN = 'o=gip-cps,c=fr'
    CAPATH = '/var/lib/calebasse/gip-cps.capath/'

LDAP_BASEDN_RSS = 'ou=339172288100045,l=Sarthe (72),' + LDAP_BASEDN
LDAP_X509_ATTR = 'userCertificate;binary'
LDAP_CA_ATTRS = {
        'cert': ('cACertificate;binary', 'CERTIFICATE'),
        'crl': ('certificateRevocationList;binary', 'X509 CRL'),
        'delta-crl': ('deltaRevocationList;binary', 'X509 CRL'),
    }

RANDFILE = '/var/tmp/randpool.dat'

if MODE_TEST:
    MAILPATH = '/var/lib/calebasse/test-mail.out/'
    MESSAGE_ID_RIGHT = 'teletransmission-test.aps42.org'
else:
    # production
    MAILPATH = '/var/lib/calebasse/mail.out/'
    MESSAGE_ID_RIGHT = 'teletransmission.aps42.org'
SENDER = 'teletransmission@aps42.org'
VVVVVV = '100500'  # ETS-DT-001-TransportsFlux_SpecsTechCommune_v1.1.pdf
NUMERO_EMETTEUR = '00000420788606'
EXERCICE = NUMERO_EMETTEUR

#
# get a certificate from gip-cps LDAP
#

def get_certificate(large_regime, dest_organism):
    """
    return a M2Crypto.X509 object, containing the certificate of the health center

    example :
      x509 = get_certificate('01', '422') # CPAM Saint Etienne
      print x509.as_text()
      print x509.as_pem()
    """
    l = ldap.initialize(LDAP_HOST)
    cn = large_regime + dest_organism + '@' + dest_organism + '.' + large_regime + '.rss.fr'
    results = l.search_s(LDAP_BASEDN_RSS, ldap.SCOPE_SUBTREE, '(cn=' + cn + ')')
    if len(results) > 1:
        raise LookupError("non unique result for cn=%s" % cn)
    if len(results) < 1:
        raise LookupError("no result for cn=%s" % cn)
    dn = results[0][0]
    attrs = results[0][1]
    if LDAP_X509_ATTR not in attrs:
        raise LookupError("no certificate in dn:%s" % dn)
    certificates = {}
    for der in results[0][1][LDAP_X509_ATTR]:
        x509 = X509.load_cert_der_string(der)
        serial = x509.get_serial_number()
        startdate =  x509.get_not_after().get_datetime().replace(tzinfo=None)
        enddate = x509.get_not_before().get_datetime().replace(tzinfo=None)
        now = datetime.utcnow().replace(tzinfo=None)
        if startdate >= now >= enddate:
            # TODO : add capath + crl validation
            # os.execute(openssl verify -CApath CAPATH -crl_check cert.pem)
            certificates[serial] = x509
    if certificates:
        return certificates[max(certificates)]
    return None

#
# IRIS/B2 mail construction
#

def mime(message):
    # compress
    if MODE_COMPRESS:
        zmessage = zlib.compress(message)
    else:
        zmessage = message
    if MODE_TEST:
        content_description = 'IRISTEST/B2'
    else:
        content_description = 'IRIS/B2'
    if MODE_COMPRESS:
        content_description += '/Z'
    return "Content-Type: application/EDI-consent\n" + \
            "Content-Transfer-Encoding: base64\n" + \
            "Content-Description: " + content_description + "\n" + \
            "\n" + base64.encodestring(zmessage).rstrip()

def smime(message, x509):
    """
    output s/mime message (headers+payload), encrypted with x509 certificate
    """
    # encrypt
    if RANDFILE:
        Rand.load_file(RANDFILE, -1)
    s = SMIME.SMIME()
    sk = X509.X509_Stack()
    sk.push(x509)
    s.set_x509_stack(sk)
    s.set_cipher(SMIME.Cipher('des_ede3_cbc'))
    bio = BIO.MemoryBuffer(message)
    pkcs7 = s.encrypt(bio)
    if RANDFILE:
        Rand.save_file(RANDFILE)
    out = BIO.MemoryBuffer()
    s.write(out, pkcs7)
    return out.read()

def build_mail(large_regime, dest_organism, b2_filename):
    """
    build a mail to healt center, with b2-compressed+encrypted information
    """
    b2_fd = open(b2_filename, 'r')
    b2 = b2_fd.read()
    b2_fd.close()

    stamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    # count invoice in the b2 file = lines start with "5"
    nb_invoices = [b2[x*128] for x in range(len(b2)/128)].count('5')

    subject = 'IR%s/%s/%s/%0.5d' % (VVVVVV, EXERCICE, stamp, nb_invoices)
    delimiter = '_ENTROUVERT-CALEBASSE-B2-%s' % stamp
    mail = {
            'From': SENDER,
            'To': large_regime + dest_organism + '@' + dest_organism + '.' + large_regime + '.rss.fr',
            'Message-ID': '<%s@%s>' % (stamp, MESSAGE_ID_RIGHT),
            'Subject': subject,
            'Mime-Version': '1.0',
            'Content-Type': 'multipart/mixed; boundary="%s"' % delimiter,
            }
    smime_part = smime(mime(b2), get_certificate(large_regime, dest_organism))

    filename = b2_filename + '-mail'
    fd = open(filename, 'w')
    for k,v in mail.items():
        fd.write('%s: %s\n' % (k,v))
    fd.write('\n')
    fd.write('--%s\n' % delimiter)
    fd.write(smime_part)
    fd.write('--%s\n' % delimiter)
    fd.close()
    return filename

#
# CApath construction
#

def der2pem(der, type_='CERTIFICATE'):
    return "-----BEGIN %s-----\n%s\n-----END %s-----\n" % \
        (type_, base64.encodestring(der).rstrip(), type_)

def build_capath(path=CAPATH):
    """
    get all pkiCA from the gip-cps.fr ldap, store them in path
    note: the gip-cps.fr ldap is limited to 10 objects in a response... by chance, there is less than 10 pkiCA ;)
    """
    l = ldap.initialize(LDAP_HOST)
    results = l.search_s(LDAP_BASEDN,ldap.SCOPE_SUBTREE,'(objectclass=pkiCA)')
    for ca in results:
        dn = ca[0]
        for attr in LDAP_CA_ATTRS:
            if LDAP_CA_ATTRS[attr][0] in ca[1]:
                n = 0
                for der in ca[1][LDAP_CA_ATTRS[attr][0]]:
                    filename = os.path.join(path, '%s.%d.%s.pem' % (dn, n, attr))
                    print "create ", filename
                    fd = open(filename, 'w')
                    fd.write(der2pem(der, LDAP_CA_ATTRS[attr][1]))
                    fd.close()
                    n += 1
    os.chdir(path)
    os.system('c_rehash .')


#
#
#


if __name__ == '__main__' and (len(sys.argv) > 1):
    action = sys.argv[1]
    if action == 'build_capath':
        build_capath()
    if action == 'x509':
        x509 = get_certificate(sys.argv[2], sys.argv[3])
        print x509.as_text()
        print x509.as_pem()
    if MODE_TEST and (action == 'test'):
        print build_mail('01', '996', 'test.b2')

