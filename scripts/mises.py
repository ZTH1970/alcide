# -*- coding: utf-8 -*-
#!/usr/bin/env python

import calebasse.settings
import django.core.management


django.core.management.setup_environ(calebasse.settings)
from calebasse.ressources.models import CodeCFTMEA

db="./scripts/MISES.TXT"

f = open(db, 'r')
for line in f.readlines()[1:]:
    words = line.split('\t')
    c = CodeCFTMEA(name=words[3].strip("\r\n").decode('iso-8859-13'),
        axe=int(words[2]), code=int(words[1]))
    c.save()
    print c
