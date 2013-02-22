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
        qs = qs.filter(patient__service=self.service)
        qs = qs.filter(date=self.date)
        self.search_form = forms.ActSearchForm(data=self.request.GET or None)
        last_name = self.request.GET.get('last_name')
        patient_record_id = self.request.GET.get('patient_record_id')
        social_security_number = self.request.GET.get('social_security_number')
        doctor_name = self.request.GET.get('doctor_name')
        filters = self.request.GET.getlist('filters')
        if last_name:
            print last_name
            qs = qs.filter(patient__last_name__istartswith=last_name)
        if patient_record_id:
            qs = qs.filter(patient__id=int(patient_record_id))
        if doctor_name:
            qs = qs.filter(doctors__last_name__icontains=doctor_name)
        if 'lost' in filters:
            qs = qs.filter(is_lost=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(ActListingView, self).get_context_data(**kwargs)
        ctx['search_form'] = self.search_form
        return ctx

act_listing = ActListingView.as_view()
act_new = agenda_views.NewAppointmentView.as_view()
