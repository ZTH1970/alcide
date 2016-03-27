# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os, sys
import csv
import codecs
import string
import random
from datetime import datetime, time

import django.core.management
import alcide.settings
django.core.management.setup_environ(alcide.settings)

from alcide.dossiers.models import PatientRecord

def main():
    i = PatientRecord.objects.all().count()
    sys.stdout.write('%d' %i)
    sys.stdout.flush()
    for patient in PatientRecord.objects.all():
        if patient.old_old_id:
            patient.paper_id = patient.old_old_id
            patient.save()
        i -= 1
        if not (i % 100):
            sys.stdout.write('%d' %i)
        else:
            sys.stdout.write('.')
        sys.stdout.flush()
if __name__ == "__main__":
    main()
