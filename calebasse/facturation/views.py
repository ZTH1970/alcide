# -*- coding: utf-8 -*-

from datetime import date

from django.http import HttpResponseRedirect

from calebasse.cbv import TemplateView, UpdateView

from models import Invoicing


class FacturationHomepageView(TemplateView):

    template_name = 'facturation/index.html'

    def get_context_data(self, **kwargs):
        context = super(FacturationHomepageView, self).get_context_data(**kwargs)
        current = Invoicing.objects.current_for_service(self.service)
        last = Invoicing.objects.last_for_service(self.service)
        context['current'] = current
        context['last'] = last
        return context

class FacturationDetailView(UpdateView):

    context_object_name = "invoicing"
    model = Invoicing
    template_name = 'facturation/detail.html'

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect('/')

    def get_context_data(self, **kwargs):
        context = super(FacturationDetailView, self).get_context_data(**kwargs)
        if self.service.name == 'CAMSP':
            (acts_not_locked, days_not_locked, acts_not_valide,
            acts_not_billable, acts_bad_state,
            acts_accepted) = context['invoicing'].list_for_billing()
        elif self.service.name == 'CMPP':
            (acts_not_locked, days_not_locked, acts_not_valide,
            acts_not_billable, acts_diagnostic, acts_treatment,
            acts_losts) = context['invoicing'].list_for_billing()
        elif 'SESSAD' in self.service.name:
            (acts_not_locked, days_not_locked, acts_not_valide,
            acts_not_billable, acts_bad_state, acts_missing_valid_notification,
            acts_accepted) = context['invoicing'].list_for_billing()
        return context

#TODO: Invoicing summary
# Missing function to generate bill from acts grouped
# Prepare stats

#TODO: Validate facturation
# generate bills

#TODO: Display the invoicing display

#TODO: Summary tab on module index

class CloseFacturationView(UpdateView):

    context_object_name = "invoicing"
    model = Invoicing
    template_name = 'facturation/close.html'

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        #TODO: grab the date
        invoicing = None
        if pk is not None:
            invoicing = Invoicing.objects.get(pk=pk, service=self.service)
        if not invoicing or self.service.name != 'CMPP' or \
                invoicing.status != Invoicing.STATUS.open:
            return HttpResponseRedirect('..')
        #TODO: give the closing date
        invoicing.close()
        return HttpResponseRedirect('..')

    def get_context_data(self, **kwargs):
        context = super(CloseFacturationView, self).get_context_data(**kwargs)
        today = date.today()
        context['date'] = date(day=today.day, month=today.month, year=today.year)
        return context
