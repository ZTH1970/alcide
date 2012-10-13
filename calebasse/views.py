# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.template.defaultfilters import slugify

SERVICES = ( u'CMPP', u'CAMSP', u'SESSAD TED', u'SESSAD DYS' )

SERVICES_MAP = dict(((slugify(s), s) for s in SERVICES))

APPLICATIONS = (
        (u'Gestion des dossiers', 'dossiers'),
        (u'Agenda', 'agenda'),
        (u'Saisie des actes', 'actes'),
        (u'Facturation et décompte', 'facturation'),
        (u'Gestion des personnes', 'personnes'),
        (u'Gestion des ressources', 'ressources'),
)

def homepage(request, service, services=SERVICES, applications=APPLICATIONS,
        template_name='calebasse/homepage.html'):
    services = [ (s, slugify(s)) for s in services]
    services_map = dict(((b, a) for a, b in services ))
    return render(request, template_name, {
        'applications': applications,
        'services': services,
        'service': service,
        'service_name': services_map.get(service),
    })

