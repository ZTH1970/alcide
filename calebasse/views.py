# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify

from cbv import HOME_SERVICE_COOKIE, TemplateView

from calebasse.ressources.models import Service

APPLICATIONS = (
        (u'Gestion des dossiers', 'dossiers'),
        (u'Agenda', 'agenda'),
#        (u'Saisie des actes', 'actes'),
#        (u'Facturation et décompte', 'facturation'),
        (u'Gestion des personnes', 'personnes'),
        (u'Gestion des ressources', 'ressources'),
)

def redirect_to_homepage(request):
    service_name = request.COOKIES.get(HOME_SERVICE_COOKIE, 'cmpp').lower()
    return redirect('homepage', service=service_name)

class Homepage(TemplateView):
    template_name='calebasse/homepage.html'

    def get_context_data(self, **kwargs):
        services = Service.objects.values_list('name', 'slug')
        services = sorted(services, key=lambda tup: tup[0])
        ctx = super(Homepage, self).get_context_data(**kwargs)
        ctx.update({
            'applications': APPLICATIONS,
            'services': services,
            'service_name': self.service.name,
        })
        return ctx

homepage = Homepage.as_view()
