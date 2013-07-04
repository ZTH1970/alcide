# -*- coding: utf-8 -*-

from calebasse import cbv
from calebasse.facturation import forms

from datetime import date, datetime

from django.http import HttpResponseRedirect, HttpResponse
from django.core.files import File

from calebasse.cbv import TemplateView, UpdateView

from models import Invoicing, Invoice
from calebasse.ressources.models import Service
from invoice_header import render_invoicing
from b2 import b2_is_configured, get_all_infos, buildall, sendmail
from noemie import noemie_mails, noemie_from_mail

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

class FacturationRebillView(cbv.FormView):
    template_name = 'facturation/rebill.html'
    form_class = forms.FacturationRebillForm
    success_url = '../..'

    def post(self, request, *args, **kwarg):
        return super(FacturationRebillView, self).post(request, *args, **kwarg)

    def form_valid(self, form):
        invoice = Invoice.objects.get(id=form.data['invoice_id'])
        for act in invoice.acts.all():
            act.is_billed = False
            act.healthcare = None
            act.save()
        invoice.rejected = True
        invoice.save()
        return super(FacturationRebillView, self).form_valid(form)

rebill_form = FacturationRebillView.as_view()

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
                len_acts_lost, len_patient_with_lost_acts, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused, len_acts_losts_missing_policy,
                len_patient_with_lost_acts_missing_policy,
                len_acts_losts_missing_birthdate,
                len_patient_with_lost_acts_missing_birthdate) = \
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
            context['len_acts_losts_missing_policy'] = len_acts_losts_missing_policy
            context['len_patient_with_lost_acts_missing_policy'] = len_patient_with_lost_acts_missing_policy
            context['len_acts_losts_missing_birthdate'] = len_acts_losts_missing_birthdate
            context['len_patient_with_lost_acts_missing_birthdate'] = len_patient_with_lost_acts_missing_birthdate
            context['some_stats'] = context['invoicing'].get_stats_per_price_per_year()
            context['batches'] = context['invoicing'].get_batches()
        elif self.service.name == 'CAMSP':
            (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause, patients_stats,
                days_not_locked, len_patient_acts_paused,
                len_acts_paused, patients_missing_policy) = \
                    context['invoicing'].get_stats_or_validate()
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
            context['patients_missing_policy'] = patients_missing_policy
        elif 'SESSAD' in self.service.name:
            (len_patient_pause, len_patient_hors_pause,
                len_acts_pause, len_acts_hors_pause,
                len_patient_missing_notif, len_acts_missing_notif,
                patients_stats, days_not_locked,
                len_patient_acts_paused, len_acts_paused,
                patients_missing_policy, patients_missing_notif) = \
                    context['invoicing'].get_stats_or_validate()
            if context['invoicing'].status == Invoicing.STATUS.closed and \
                    date.today() > context['invoicing'].end_date:
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
            context['patients_missing_policy'] = patients_missing_policy
            context['patients_missing_notif'] = patients_missing_notif
        return context


class CloseInvoicingView(cbv.FormView):
    template_name = 'facturation/close.html'
    form_class = forms.CloseInvoicingForm
    success_url = '..'

    def post(self, request, *args, **kwarg):
        return super(CloseInvoicingView, self).post(request, *args, **kwarg)

    def form_valid(self, form):
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

class FacturationDownloadView(cbv.DetailView):
    context_object_name = "invoicing"
    model = Invoicing

    def get(self, *args, **kwargs):
        invoicing = self.get_object()
        path = render_invoicing(invoicing, delete=False)
        content = File(file(path))
        response = HttpResponse(content,'application/pdf')
        response['Content-Length'] = content.size
        response['Content-Disposition'] = 'attachment; filename="facturation-%s.pdf"' % invoicing.seq_id
        return response

class FacturationExportView(cbv.DetailView):
    context_object_name = "invoicing"
    model = Invoicing

    def get(self, *args, **kwargs):
        invoicing = self.get_object()
        path = invoicing.export_for_accounting()
        content = File(file(path))
        response = HttpResponse(content,'text/plain')
        response['Content-Length'] = content.size
        response['Content-Disposition'] = 'attachment; filename="export-%s.txt"' % invoicing.seq_id
        return response


class FacturationTransmissionView(UpdateView):
    context_object_name = "invoicing"
    model = Invoicing
    template_name = 'facturation/transmission.html'

    def get_context_data(self, **kwargs):
        context = super(FacturationTransmissionView, self).get_context_data(**kwargs)
        context['b2_is_configured'] = b2_is_configured()
        try:
            context['b2'] = get_all_infos(context['invoicing'].seq_id)
        except IOError, e:
            context['error_message'] = e
        return context

class FacturationTransmissionBuildView(cbv.DetailView):
    context_object_name = "invoicing"
    model = Invoicing

    def get(self, *args, **kwargs):
        invoicing = self.get_object()
        if b2_is_configured() and invoicing.status == "validated":
            buildall(invoicing.seq_id)
        return HttpResponseRedirect('..')

class FacturationTransmissionMailView(UpdateView):
    context_object_name = "invoicing"
    model = Invoicing

    def get(self, *args, **kwargs):
        invoicing = self.get_object()
        if b2_is_configured() and invoicing.status == "validated":
            sendmail(invoicing.seq_id, oneb2=kwargs.get('b2'))
        return HttpResponseRedirect('..')


class FacturationNoemieView(TemplateView):
    template_name = 'facturation/noemie.html'

    def get_context_data(self, **kwargs):
        context = super(FacturationNoemieView, self).get_context_data(**kwargs)
        context['b2_is_configured'] = b2_is_configured()
        if b2_is_configured():
            name = kwargs.get('name')
            try:
                if name:
                    context['noemie'] = noemie_from_mail(name)
                else:
                    context['noemies'] = noemie_mails()
            except IOError, e:
                context['error_message'] = e
        return context
