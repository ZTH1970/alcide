import datetime

from django.shortcuts import redirect

from calebasse.cbv import ListView
from calebasse.agenda import views as agenda_views

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
        self.get_search_form()
        qs = qs.filter(patient__service=self.service)
        qs = qs.filter(date=self.date)
        if self.request.method == 'POST' and self.search_form.is_valid():
            cd = self.search_form.cleaned_data
            last_name = cd['last_name']
            if last_name:
                qs = qs.filter(patient__last_name__icontains=last_name)
            patient_record_id = cd['patient_record_id']
            if patient_record_id:
                qs = qs.filter(patient__id=int(patient_record_id))
            social_security_number = cd['social_security_number']
            # FIXME: what to do with the ssn ?
            doctor_name = cd['doctor_name']
            if doctor_name:
                qs = qs.filter(doctors__last_name__icontains=doctor_name)
            filters = cd['filters']
            if 'non-invoicable' in filters:
                pass # FIXME
            if 'absent-or-canceled' in filters:
                pass # FIXME
            if 'lost' in filters:
                pass # FIXME
            if 'invoiced' in filters:
                pass # FIXME
            if 'last-invoicing' in filters:
                pass # FIXME
            if 'current-invoicing' in filters:
                pass # FIXME
        return qs

    def get_search_form(self):
        if self.request.method == 'POST':
            self.search_form = forms.ActSearchForm(data=self.request.POST)
        else:
            self.search_form = forms.ActSearchForm()
        return self.search_form

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ActListingView, self).get_context_data(**kwargs)
        ctx['search_form'] = self.search_form
        return ctx

act_listing = ActListingView.as_view()
act_new = agenda_views.NewAppointmentView.as_view()
