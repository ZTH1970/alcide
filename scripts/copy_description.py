# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os

log = open('descriptions.log', 'a+')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calebasse.settings")

from calebasse.agenda.models import EventWithAct

for event in EventWithAct.objects.all():
    if event.act:
        if not event.act.comment and event.description:
            event.act.comment = event.description
            event.act.save()
        if event.act.comment and event.description \
           and (event.act.comment != event.description):
            log.write("acte : %s\n" % event.act.comment.encode('utf-8'))
            log.write("evenement (%d) : %s\n\n" % (event.id, event.description.encode('utf-8')))
            event.act.comment = event.description
            event.act.save()

log.close()
