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
        if self.service.name == 'CMPP':
            (len_patients, len_invoices, len_invoices_hors_pause,
            len_acts_invoiced, len_acts_invoiced_hors_pause,
            len_patient_invoiced, len_patient_invoiced_hors_pause,
            len_acts_lost, len_patient_with_lost_acts,
            patients_stats, days_not_locked) = \
            context['invoicing'].get_stats_or_validate()
            context['len_patients'] = len_patients
            context['len_invoices'] = len_invoices
            context['len_invoices_hors_pause'] = len_invoices_hors_pause
            context['len_invoices_pause'] = len_invoices - len_invoices_hors_pause
            context['len_acts_invoiced'] = len_acts_invoiced
            context['len_acts_invoiced_hors_pause'] = len_acts_invoiced_hors_pause
            context['len_acts_invoiced_pause'] = len_acts_invoiced - len_acts_invoiced_hors_pause
            context['len_patient_invoiced'] = len_patient_invoiced
            context['len_patient_invoiced_hors_pause'] = len_patient_invoiced_hors_pause
            context['len_patient_invoiced_pause'] = len_patient_invoiced - len_patient_invoiced_hors_pause
            context['len_acts_lost'] = len_acts_lost
            context['len_patient_with_lost_acts'] = len_patient_with_lost_acts
            context['patients_stats'] = patients_stats
            context['days_not_locked'] = days_not_locked
        elif self.service.name == 'CAMSP':
            (acts_not_locked, days_not_locked, acts_not_valide,
            acts_not_billable, acts_diagnostic, acts_treatment,
            acts_losts) = context['invoicing'].invoicing.get_stats_or_validate()
        elif 'SESSAD' in self.service.name:
            (acts_not_locked, days_not_locked, acts_not_valide,
            acts_not_billable, acts_bad_state, acts_missing_valid_notification,
            acts_accepted) = context['invoicing'].invoicing.get_stats_or_validate()
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
