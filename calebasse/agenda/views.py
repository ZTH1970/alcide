import datetime

from django.shortcuts import redirect

from calebasse.cbv import TemplateView
from calebasse.personnes.models import Worker

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect('agenda', date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)

class AgendaHomepageView(TemplateView):
    template_name = 'agenda/index.html'

    def get_context_data(self, **kwargs):
        context = super(AgendaHomepageView, self).get_context_data(**kwargs)
        #context['therapeutes'] = Therapeute.objects.for_service(self.service)
        #context['personnels'] = Personnel.objects.for_service(self.service)
        return context
