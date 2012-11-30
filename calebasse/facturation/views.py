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
            (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause, acts_accepted,
                days_not_locked) = context['invoicing'].get_stats_or_validate()
            if context['invoicing'].status == Invoicing.STATUS.closed and \
                    date.today() > context['invoicing'].end_date:
                context['show_validation_btn'] = True
            context['len_patient_pause'] = len_patient_pause
            context['len_patient_hors_pause'] = len_patient_hors_pause
            context['len_acts_pause'] = len_acts_pause
            context['len_acts_hors_pause'] = len_acts_hors_pause
            context['acts_accepted'] = acts_accepted
            context['days_not_locked'] = days_not_locked
        elif 'SESSAD' in self.service.name:
            (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause,
                len_patient_missing_notif, len_acts_missing_notif,
                acts_accepted, days_not_locked) = context['invoicing'].get_stats_or_validate()
            if context['invoicing'].status == Invoicing.STATUS.closed and \
                    date.today() > context['invoicing'].end_date:
                context['show_validation_btn'] = True
            context['len_patient_pause'] = len_patient_pause
            context['len_patient_hors_pause'] = len_patient_hors_pause
            context['len_acts_pause'] = len_acts_pause
            context['len_acts_hors_pause'] = len_acts_hors_pause
            context['len_patient_missing_notif'] = len_patient_missing_notif
            context['len_acts_missing_notif'] = len_acts_missing_notif
            context['acts_accepted'] = acts_accepted
            context['days_not_locked'] = days_not_locked
        return context


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

class ValidationFacturationView(UpdateView):

    context_object_name = "invoicing"
    model = Invoicing
    template_name = 'facturation/validation.html'

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        invoicing = None
        if pk is not None:
            invoicing = Invoicing.objects.get(pk=pk, service=self.service)
        if not invoicing or \
                invoicing.status != Invoicing.STATUS.closed:
            return HttpResponseRedirect('..')
        invoicing.get_stats_or_validate(commit=True)
        return HttpResponseRedirect('..')

    def get_context_data(self, **kwargs):
        context = super(ValidationFacturationView, self).get_context_data(**kwargs)
        return context
