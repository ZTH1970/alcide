import datetime

from django.shortcuts import redirect

from calebasse.cbv import TemplateView
from calebasse.agenda.models import Occurrence
from calebasse.personnes.models import Worker
from calebasse.ressources.models import WorkerType

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect('agenda', date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)

class AgendaHomepageView(TemplateView):

    template_name = 'agenda/index.html'

    def get_context_data(self, **kwargs):
        context = super(AgendaHomepageView, self).get_context_data(**kwargs)
        context['workers_types'] = []
        context['workers_agenda'] = []
        context['disponnibility'] = {}
        workers = []
        for worker_type in WorkerType.objects.all():
            data = {'type': worker_type.name, 'workers': Worker.objects.for_service(self.service, worker_type) }
            context['workers_types'].append(data)
            workers.extend(data['workers'])

        for worker in workers:
            context['workers_agenda'].append({'worker': worker,
                    'agenda': Occurrence.objects.daily_occurrences(context['date'], [worker])})

        context['disponnibility'] = Occurrence.objects.daily_disponiblity(context['date'], context['workers'])
        return context
