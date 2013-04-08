# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv

from datetime import datetime, time, date

import calebasse.settings
import django.core.management
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

django.core.management.setup_environ(calebasse.settings)

from django.contrib.auth.models import User

from calebasse.ressources.models import ManagementCode

# Configuration
db = "./scripts/20121221-192258/F_ST_ETIENNE_SESSAD_TED"


def _to_date(str_date):
    if not str_date:
        return None
    return datetime.strptime(str_date[:-13], "%Y-%m-%d")

def _to_int(str_int):
    if not str_int:
        return None
    return int(str_int)

def main():
        l = []
        csvfile = open(os.path.join(db, 'codes_gestion.csv'), 'rb')
        csvlines = csv.reader(csvfile, delimiter=';', quotechar='|')
        cols = csvlines.next()
        for line in csvlines:
            ManagementCode(old_id=line[0], code=line[1], name=line[2].decode('utf-8')).save()
        csvfile.close()

if __name__ == "__main__":
    main()
