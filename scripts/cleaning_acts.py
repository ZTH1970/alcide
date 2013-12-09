# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import datetime


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calebasse.settings")
log = open('acts_cleaning.log', 'a+')

i = 0
j = 0

from calebasse.agenda.models import EventWithAct

for event in EventWithAct.objects.all():
    if event.is_recurring():
        for a in event.act_set.all():
            if not event.today_occurrence(today=a.date) and \
               not a.is_billed:
                log.write("rec %d\n" % a.id)
                a.delete()
                i += 1
    else:
        if event.canceled and not event.act.is_billed \
           and event.act.id:
            try:
               log.write("%d\n" % event.act.id)
               event.act.delete()
               j += 1
            except:
               pass

print "acte sup %d recurrence" % i
print "acte sup %d canceled" % j

log.close()

