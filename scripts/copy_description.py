# -*- coding: utf-8 -*-
#!/usr/bin/env python

import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from calebasse.agenda.models import EventWithAct

for event in EventWithAct.objects.all():
    if not event.act.comment and event.description:
        event.act.comment = event.description
        event.act.save()
