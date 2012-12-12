# -*- coding: utf-8 -*-
#!/usr/bin/env python

import csv
import codecs

import calebasse.settings
import django.core.management


django.core.management.setup_environ(calebasse.settings)
from calebasse.ressources.models import HealthCenter, LargeRegime

db="./scripts/CPAM.csv"

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="iso8859-15", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

def main():
    csvfile = open(db, 'rb')
    csvlines = UnicodeReader(csvfile, delimiter=';', quotechar='"')
    cols = csvlines.next()
    i = 2
    for line in csvlines:
        print i
        try:
            regime = LargeRegime.objects.get(code=line[0])
        except Exception, e:
            print "%s for %s in %s" % (str(e), line[0], str(line))
        else:
            if len(line) != 14:
                print "Error check your csv file"
            city = line[9]
            if line[11]:
                city += ' ' + line[11]
            center, created = HealthCenter.objects.get_or_create(
                    large_regime=regime,
                    code=line[2],
                    name=line[3],
                    dest_organism=line[5],
                    computer_center_code=line[6],
                    address=line[7],
                    address_complement=line[8],
                    city=city,
                    zip_code=line[10],
                    phone=line[12],
                    fax=line[13],
                    health_fund=line[1])
        i += 1
    csvfile.close()


if __name__ == "__main__":
    main()
