# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import os.path
import csv
import codecs
import string
import random
from glob import glob
from datetime import datetime, time

import django.core.management
import alcide.settings
django.core.management.setup_environ(alcide.settings)

from alcide.ressources.models import ActType, Service

def _to_int(str_int):
    if not str_int:
        return None
    return int(str_int)

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
    ActType.objects.all().delete()
    for path in glob('./scripts/types_d_actes/*.csv'):
        filename = os.path.basename(path)
        service = Service.objects.get(name=filename[12:-4].replace('_', ' '))
        csvfile = open(path, 'rb')
        csvlines = UnicodeReader(csvfile, delimiter=',', quotechar='"',encoding='utf-8')
        for line in csvlines:
            a = ActType.objects.create(service=service,
                    old_id=line[0],
                    name=line[1],
                    billable=not bool(line[2]),
                    display_first=bool(line[3]))
            print a.id, a.old_id, a.name, a.service


if __name__ == "__main__":
    main()
