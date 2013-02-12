# -*- coding: utf-8 -*-

import tempfile
import subprocess
from fdfgen import forge_fdf

class InvoiceTemplate(object):
    NUM_FINESS = u'n° finess'
    IDENTIFICATION_ETABLISSEMENT = u'identification établissement'
    NUM_LOT = u'n°lot'
    NUM_FACTURE = u'n°facture'
    NUM_ENTREE = u'n°entrée'
    NUM_FEUILLET = u'n°feuillet'
    DATE_ELABORATION = u'date élaboration'
    NOM_BENEFICIAIRE = u'nom bénéficiaire'
    DATE_NAISSANCE_RANG = u'date naissance+rang'
    CODE_ORGANISME = u'code organisme'
    DATE_ENTREE = u'date entrée'
    DATE_PRESENCE = u'date présence'
    DATE_SORTIE = u'date sortie'
    NOM_ASSURE = u'nom assuré'
    IMMAT_CLE = u'immat+clé'
    ADRESSE1 = u'adresse1'
    ADRESSE2 = u'adresse2'
    NUM_OU_DATE_AT = u'n° ou date AT'
    DATE_ACCIDENT = u'date accident'
    MAX_LINES = 24 # i + 1
    MT = u'MT%d'   # mode de traitement
    DMT = u'DMT%d' # discipline médico-tarifaire
    PR = u'PR%d'   # prestation

    DATE_DEBUT = u'DATE%d' # % i*2+1
    DATE_FIN = u'DATE%d' # i*2+2
    PRIX = u'PRIX%d' # prix
    QUANT = u'QUANT%d' # quantite
    MONTANT = u'MONTANT%d' # montant
    SOUSTOTAL1 = u'SOUSTOTAL1'
    SOUSTOTAL2 = u'SOUSTOTAL2'
    TOTAL1 = u'TOTAL1'
    TOTAL2 = u'TOTAL2'

    ABSENCE_SIGNATURE = (u'absence signature', 'Oui')
    PRISE_EN_CHARGE = (u'prise en charge', 'AT', 'L 115', 'accident tiers')
    ACCIDENT_CAUSE_TIERS = (u'accident causé tiers', 'non')
    PART_OBLIG = (u'PART OBLIG', 'Oui')
    PART_COMPL = (u'PART COMPL', 'Oui')
    buttons = [ ABSENCE_SIGNATURE, PRISE_EN_CHARGE, ACCIDENT_CAUSE_TIERS, 
            PART_OBLIG, PART_COMPL ]

    def __init__(self, template_path=None, flatten=False):
        self.template_path = template_path
        self.fields = {}
        self.flatten = False
        self.stack = []
        self.i = 0

    def push(self):
        self.stack.append(self.fields.copy())

    def pop(self):
        self.fields = self.stack.pop()

    def peek(self):
        self.fields = self.stack[-1].copy()

    def feed(self, field, value):
        self.fields[field] = value

    def feed_line(self, mt, dmt, prestation, date_debut, date_fin, prix, quant, montant):
        i = self.i + 1
        k = self.i * 2 + 1
        j = self.i * 2 + 2
        self.feed(self.MT % i, mt)
        self.feed(self.DMT % i, dmt)
        self.feed(self.PR % i, prestation)
        self.feed(self.DATE_DEBUT % k, date_debut)
        self.feed(self.DATE_FIN % j, date_fin)
        self.feed(self.PRIX % i, prix)
        self.feed(self.QUANT % i, quant)
        self.feed(self.MONTANT % i, montant)
        self.i += 1

    def get_pdftk_path(self):
        return '/usr/bin/pdftk'

    def get_template_path(self):
        return self.template_path or 'template.pdf'

    def generate(self, flatten=False):
        flatten = self.flatten or flatten
        string_fields = []
        other_fields = []
        for k, v in self.fields.iteritems():
            if isinstance(k, basestring):
                string_fields.append((k, v))
            else:
                other_fields.append((k[0], k[1] if isinstance(v, bool) else v))
        fdf = forge_fdf("", string_fields, other_fields, [], [])
        with tempfile.NamedTemporaryFile() as temp_fdf:
            with tempfile.NamedTemporaryFile() as temp_out_pdf:
                temp_fdf.write(fdf)
                temp_fdf.flush()
                args = [self.get_pdftk_path(), 
                    self.template_path, 'fill_form',
                    temp_fdf.name, 'output', temp_out_pdf.name]
                if flatten:
                    args.append('flatten')
                proc = subprocess.Popen(args)
                proc.wait()
                temp_fdf.close()
                return temp_out_pdf.read()

if __name__ == '__main__':
    import sys
    import locale

    locale.setlocale(locale.LC_ALL, '')
    locale_encoding = locale.nl_langinfo(locale.CODESET)
    try:
        infile = sys.argv[1]
        outfile = sys.argv[2]
        args = sys.argv[3:]
    except IndexError:
        print 'Usage: python', __file__, 'template.pdf outfile.pdf NOM_BENFICIAIRE="Benjamin Dauvergne"'
    tpl = InvoiceTemplate(infile)
    for arg in args:
        key, value = arg.split('=')
        key = getattr(InvoiceTemplate, key)
        value = unicode(value, locale_encoding)
        tpl.feed(key, value)
    with open(outfile, 'w') as f:
        f.write(tpl.generate())
