# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.views.generic.edit import ModelFormMixin
from django.shortcuts import redirect

from calebasse.cbv import ListView, UpdateView, FormView, DeleteView
from calebasse.agenda.views import NewAppointmentView

import copy
import models
import forms

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect(act_listing, date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)

class ActListingView(ListView):
    model=models.Act
    template_name='actes/act_listing.html'

    def get_queryset(self):
        qs = super(ActListingView, self).get_queryset()
        qs = qs.filter(patient__service=self.service)
        qs = qs.filter(date=self.date)
        self.search_form = forms.ActSearchForm(data=self.request.GET or None)
        last_name = self.request.GET.get('last_name')
        patient_record_id = self.request.GET.get('patient_record_id')
        social_security_number = self.request.GET.get('social_security_number')
        doctor_name = self.request.GET.get('doctor_name')
        filters = self.request.GET.getlist('filters')
        if last_name:
            qs = qs.filter(patient__last_name__istartswith=last_name)
        if patient_record_id:
            qs = qs.filter(patient__id=int(patient_record_id))
        if doctor_name:
            qs = qs.filter(doctors__last_name__icontains=doctor_name)
        if 'valide' in filters:
            qs = qs.exclude(last_validation_state__state_name__exact='VALIDE')
        if 'pointe' in filters:
            qs = qs.filter(last_validation_state__isnull=False). \
                    exclude(last_validation_state__state_name__exact='NON_VALIDE')
        if 'non-pointe' in filters:
            qs = qs.filter(Q(last_validation_state__isnull=True) | \
                    Q(last_validation_state__state_name__exact='NON_VALIDE'))
        if 'absent-or-canceled' in filters:
            qs = qs.filter(last_validation_state__state_name__in=('ABS_NON_EXC',
                'ABS_EXC', 'ABS_INTER', 'ANNUL_NOUS',
                'ANNUL_FAMILLE', 'REPORTE', 'ABS_ESS_PPS', 'ENF_HOSP'))
        if 'is-billable' in filters:
            qs = qs.filter(
                    (Q(act_type__billable=True) & Q(switch_billable=False)) | \
                    (Q(act_type__billable=False) & Q(switch_billable=True))
                    )
        if 'switch-billable' in filters:
            qs = qs.filter(switch_billable=True)
        if 'lost' in filters:
            qs = qs.filter(is_lost=True)
        if 'pause-invoicing' in filters:
            qs = qs.filter(pause=True)
        if 'invoiced' in filters:
            qs = qs.filter(is_billed=True)

        return qs.select_related()

    def get_context_data(self, **kwargs):
        ctx = super(ActListingView, self).get_context_data(**kwargs)
        ctx['search_form'] = self.search_form
        return ctx

class NewAct(NewAppointmentView):
    success_url = '.'
    success_msg = u'Acte enregistré avec succès.'

    def form_valid(self, form):
        result = super(NewAct, self).form_valid(form)
        self.object.act.save()
        return result

act_listing = ActListingView.as_view()
act_new = NewAct.as_view()

class DeleteActView(DeleteView):
    model = models.Act
    template_name = 'actes/confirm_delete.html'
    success_url = '..'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.event:
            self.object.event.delete()
        if not self.object.is_billed:
            self.object.delete()

        return HttpResponse(status=204)

delete_act = DeleteActView.as_view()

class UpdateActView(UpdateView):
    model = models.Act
    form_class = forms.ActUpdate
    template_name = 'actes/act_update.html'
    success_url = '..'

    def form_valid(self, form):
        result = super(UpdateView, self).form_valid(form)
        if self.object.event:
            doctors = copy.copy(self.object.doctors.all())
            self.object.event.participants =  doctors
            self.object.event.act_type =  act_type
            self.object.save()
        return result

update_act = UpdateActView.as_view()

class RebillActView(UpdateView):
    model = models.Act
    template_name = 'actes/act_rebill.html'
    success_url = '..'

    def post(self, request, *args, **kwarg):
        act = models.Act.objects.get(pk=kwarg['pk'])
        act.is_billed = False
        act.healthcare = None
        act.save()
        return super(RebillActView, self).post(request, *args, **kwarg)

rebill_act = RebillActView.as_view()
