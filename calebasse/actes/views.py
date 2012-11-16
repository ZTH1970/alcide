import datetime

from django.shortcuts import redirect

from calebasse.cbv import ListView

import models

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect(act_listing, date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)

class ActListingView(ListView):
    model=models.EventAct
    template_name='actes/act_listing.html'

    def get_queryset(self):
        qs = super(ActListingView, self).get_queryset()
        qs.filter(services=self.service)
        return qs

act_listing = ActListingView.as_view()
