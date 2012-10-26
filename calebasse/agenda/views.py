import datetime

from django.db.models import Q
from django.shortcuts import redirect

from calebasse.cbv import TemplateView, CreateView
from calebasse.agenda.models import Occurrence
from calebasse.personnes.models import TimeTable
from calebasse.actes.models import EventAct
from calebasse.agenda.appointments import get_daily_appointments
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service, WorkerType

from forms import NewAppointmentForm

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect('agenda', date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)

class AgendaHomepageView(TemplateView):

    template_name = 'agenda/index.html'

    def get_context_data(self, **kwargs):
        context = super(AgendaHomepageView, self).get_context_data(**kwargs)

        weekday_mapping = {
                '0': u'dimanche',
                '1': u'lundi',
                '2': u'mardi',
                '3': u'mercredi',
                '4': u'jeudi',
                '5': u'vendredi',
                '6': u'samedi'
                }
        weekday = weekday_mapping[context['date'].strftime("%w")]
        time_tables = TimeTable.objects.select_related('worker').\
                filter(service=self.service).\
                filter(weekday=weekday).\
                filter(start_date__lte=context['date']).\
                filter(Q(end_date=None) |Q(end_date__gte=context['date'])).\
                order_by('start_date')
        occurrences = Occurrence.objects.daily_occurrences(context['date']).order_by('start_time')

        context['workers_types'] = []
        context['workers_agenda'] = []
        context['disponnibility'] = {}
        workers = []
        for worker_type in WorkerType.objects.all():
            data = {'type': worker_type.name, 'workers': Worker.objects.for_service(self.service, worker_type) }
            context['workers_types'].append(data)
            workers.extend(data['workers'])

        occurrences_workers = {}
        for worker in workers:
            time_tables_worker = [tt for tt in time_tables if tt.worker.id == worker.id]
            occurrences_worker = [o for o in occurrences if worker.id in o.event.participants.values_list('id', flat=True)]
            occurrences_workers[worker.id] = occurrences_worker
            context['workers_agenda'].append({'worker': worker,
                    'appointments': get_daily_appointments(context['date'], worker, self.service,
                        time_tables_worker, occurrences_worker)})

        context['disponibility'] = Occurrence.objects.daily_disponiblity(context['date'],
                occurrences_workers, workers)
        return context

class NewAppointmentView(CreateView):
    model = EventAct
    form_class = NewAppointmentForm
    template_name = 'agenda/nouveau-rdv.html'
    success_url = '..'

    def get_initial(self):
        initial = super(NewAppointmentView, self).get_initial()
        initial['date'] = self.kwargs.get('date')
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        return initial

    def get_form_kwargs(self):
        kwargs = super(NewAppointmentView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs

    def post(self, *args, **kwargs):
        return super(NewAppointmentView, self).post(*args, **kwargs)

def new_appointment(request):
    pass

