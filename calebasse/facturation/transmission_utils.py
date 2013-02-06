#!/usr/bin/env python

import os
import sys
import ldap
from M2Crypto import X509, SSL
from datetime import datetime
import base64

LDAP_HOST = 'ldap://annuaire.gip-cps.fr'
LDAP_BASEDN = 'o=gip-cps,c=fr'
LDAP_BASEDN_RSS = 'ou=339172288100045,l=Sarthe (72),' + LDAP_BASEDN
LDAP_X509_ATTR = 'userCertificate;binary'
LDAP_CA_ATTRS = {
        'cert': ('cACertificate;binary', 'CERTIFICATE'),
        'crl': ('certificateRevocationList;binary', 'X509 CRL'),
        'delta-crl': ('deltaRevocationList;binary', 'X509 CRL'),
    }
CAPATH = '/var/lib/calebasse/gie-cps.capath/'

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
            # CAPATH = '/tmp/gie-cps.capath/'
            # os.execute(openssl verify -CApath CAPATH -crl_check cert.pem)
            certificates[serial] = x509
    if certificates:
        return certificates[max(certificates)]
    return None


def der2pem(der, type_='CERTIFICATE'):
    return "-----BEGIN %s-----\n%s\n-----END %s-----\n" % \
        (type_, base64.encodestring(der).rstrip(), type_)

def build_capath(path):
    """
    get all pkiCA from the gie-cps.fr ldap, store them in path
    note: the gie-cps.fr ldap is limited to 10 objects in a response... by chance, there is less than 10 pkiCA ;)
    """
    l = ldap.initialize(LDAP_HOST)
    results = l.search_s(LDAP_BASEDN,ldap.SCOPE_SUBTREE,'(objectclass=pkiCA)')
    for ca in results:
        dn = ca[0]
        for attr in LDAP_CA_ATTRS:
            if LDAP_CA_ATTRS[attr][0] in ca[1]:
                for der in ca[1][LDAP_CA_ATTRS[attr][0]]:
                    filename = os.path.join(path, '%s.%s.pem' % (dn,attr))
                    print "create ", filename
                    fd = open(filename, 'w')
                    fd.write(der2pem(der, LDAP_CA_ATTRS[attr][1]))
                    fd.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        capath = sys.argv[1]
    else:
        capath = CAPATH
    print "get capath certificates in", capath
    build_capath(capath)

