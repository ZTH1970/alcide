#!/usr/bin/env python

import os
import csv

from datetime import datetime

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

# Config
db_path = "/home/jschneider/dav/temp/20121015-120922"

dbs = ["F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD", "F_ST_ETIENNE_SESSAD_TED"]
tables = ["notes", "ev"]

def _get_dict(cols, line):
    """"""
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data
    return res


def ev_mapper(data):
    """ """
    pass

def notes_mapper(data, note):
    """ """
    pass

mappers = {
        "ev": ev_mapper
        "notes": notes_mapper
        }

def main():
    """ """
    for db in dbs:
        for table in tables:
            csvfile = open(os.path.join(db_path, db, '%s.csv' % table), 'rb')
            csvlines = csv.reader(csvfile, delimiter=',', quotechar='"')
            cols = csvlines.next()
            for line in csvlines:
                data = _get_dict(cols, line)
                mappers[table](data)
            csvfile.close()


if __name__ == "__main__":
    main()

