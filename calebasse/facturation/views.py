# -*- coding: utf-8 -*-

from calebasse import cbv
from calebasse.facturation import forms

from datetime import date, datetime

from django.http import HttpResponseRedirect

from calebasse.cbv import TemplateView, UpdateView

from models import Invoicing
from calebasse.ressources.models import Service


def display_invoicing(request, *args, **kwargs):
    if request.method == 'POST':
        try:
            seq_id = request.POST.get('id', None)
            service_name = kwargs['service']
            service = Service.objects.get(slug=service_name)
            invoicing = Invoicing.objects.get(seq_id=seq_id, service=service)
            return HttpResponseRedirect('%s' % invoicing.id)
        except:
            pass
    return HttpResponseRedirect('.')

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
            patients_stats, days_not_locked, len_patient_acts_paused,
                len_acts_paused, len_acts_lost_missing_policy,
                len_patient_with_lost_acts_missing_policy) = \
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
            context['len_patient_acts_paused'] = len_patient_acts_paused
            context['len_acts_paused'] = len_acts_paused
            context['len_acts_lost_missing_policy'] = len_acts_lost_missing_policy
            context['len_patient_with_lost_acts_missing_policy'] = len_patient_with_lost_acts_missing_policy
        elif self.service.name == 'CAMSP':
            (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused) = context['invoicing'].get_stats_or_validate()
            if context['invoicing'].status == Invoicing.STATUS.closed and \
                    date.today() > context['invoicing'].end_date:
                context['show_validation_btn'] = True
            context['len_patient_pause'] = len_patient_pause
            context['len_patient_hors_pause'] = len_patient_hors_pause
            context['len_acts_pause'] = len_acts_pause
            context['len_acts_hors_pause'] = len_acts_hors_pause
            context['patients_stats'] = patients_stats
            context['days_not_locked'] = days_not_locked
            context['len_patient_acts_paused'] = len_patient_acts_paused
            context['len_acts_paused'] = len_acts_paused
        elif 'SESSAD' in self.service.name:
            (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause,
                len_patient_missing_notif, len_acts_missing_notif,
                patients_stats, days_not_locked,
                len_patient_acts_paused, len_acts_paused) = \
                    context['invoicing'].get_stats_or_validate()
            if context['invoicing'].status == Invoicing.STATUS.closed and \
                    date.today() > context['invoicing'].end_date:
                context['show_validation_btn'] = True
            #XXX: Supressimer ligne suivante
            context['show_validation_btn'] = True
            context['len_patient_pause'] = len_patient_pause
            context['len_patient_hors_pause'] = len_patient_hors_pause
            context['len_acts_pause'] = len_acts_pause
            context['len_acts_hors_pause'] = len_acts_hors_pause
            context['len_patient_missing_notif'] = len_patient_missing_notif
            context['len_acts_missing_notif'] = len_acts_missing_notif
            context['patients_stats'] = patients_stats
            context['days_not_locked'] = days_not_locked
            context['len_patient_acts_paused'] = len_patient_acts_paused
            context['len_acts_paused'] = len_acts_paused
        return context


class CloseInvoicingView(cbv.FormView):
    template_name = 'facturation/close.html'
    form_class = forms.CloseInvoicingForm
    success_url = '..'

    def post(self, request, *args, **kwarg):
        return super(CloseInvoicingView, self).post(request, *args, **kwarg)

    def form_valid(self, form):
        print form.data
        service = Service.objects.get(name=form.data['service_name'])
        invoicing = Invoicing.objects.get(id=form.data['invoicing_id'])
        date_selected = datetime.strptime(form.data['date'], "%d/%m/%Y")
        invoicing.close(end_date=date_selected)
        return super(CloseInvoicingView, self).form_valid(form)

close_form = CloseInvoicingView.as_view()


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
