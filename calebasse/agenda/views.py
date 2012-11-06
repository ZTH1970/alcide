import datetime
import collections

from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render_to_response

from calebasse.cbv import TemplateView, CreateView
from calebasse.agenda.models import Occurrence, Event, EventType
from calebasse.personnes.models import TimeTable
from calebasse.actes.models import EventAct
from calebasse.agenda.appointments import get_daily_appointments
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service, WorkerType
from calebasse.actes.validation import (are_all_acts_of_the_day_locked,
    get_acts_of_the_day)
from calebasse.actes.validation_states import VALIDATION_STATES
from calebasse.middleware.request import get_request

from forms import NewAppointmentForm, NewEventForm

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
        time_tables_workers = {}
        for worker in workers:
            time_tables_worker = [tt for tt in time_tables if tt.worker.id == worker.id]
            occurrences_worker = [o for o in occurrences if worker.id in o.event.participants.values_list('id', flat=True)]
            occurrences_workers[worker.id] = occurrences_worker
            time_tables_workers[worker.id] = time_tables_worker
            context['workers_agenda'].append({'worker': worker,
                    'appointments': get_daily_appointments(context['date'], worker, self.service,
                        time_tables_worker, occurrences_worker)})

        context['disponibility'] = Occurrence.objects.daily_disponiblity(context['date'],
                occurrences_workers, workers, time_tables_workers)
        return context

class AgendaServiceActivityView(TemplateView):

    template_name = 'agenda/service-activity.html'

    def get_context_data(self, **kwargs):
        context = super(AgendaServiceActivityView, self).get_context_data(**kwargs)

        appointments_times = dict()
        appoinment_type = EventType.objects.get(id=1)
        occurrences = Occurrence.objects.daily_occurrences(context['date'],
                services=[self.service],
                event_type=appoinment_type)
        for occurrence in occurrences:
            start_time = occurrence.start_time.strftime("%H:%M")
            if not appointments_times.has_key(start_time):
                appointments_times[start_time] = dict()
                appointments_times[start_time]['row'] = 0
                appointments_times[start_time]['appointments'] = []
            appointment = dict()
            length = occurrence.end_time - occurrence.start_time
            if length.seconds:
                length = length.seconds / 60
                appointment['length'] = "%sm" % length
            event_act = occurrence.event.eventact
            appointment['patient'] = event_act.patient.display_name
            appointment['therapists'] = ""
            for participant in occurrence.event.participants.all():
                appointment['therapists'] += participant.display_name + "; "
            if appointment['therapists']:
                appointment['therapists'] = appointment['therapists'][:-2]
            appointment['act'] = event_act.act_type.name
            appointments_times[start_time]['row'] += 1
            appointments_times[start_time]['appointments'].append(appointment)
        context['appointments_times'] = collections.OrderedDict(sorted(appointments_times.items()))
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

class NewEventView(CreateView):
    model = Event
    form_class = NewEventForm
    template_name = 'agenda/new-event.html'
    success_url = '..'

    def get_initial(self):
        initial = super(NewEventView, self).get_initial()
        initial['date'] = self.kwargs.get('date')
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        return initial

    def get_form_kwargs(self):
        kwargs = super(NewEventView, self).get_form_kwargs()
        #kwargs['service'] = self.service
        return kwargs

    def post(self, *args, **kwargs):
        return super(NewEventView, self).post(*args, **kwargs)

def new_appointment(request):
    pass

class AgendaServiceActValidationView(TemplateView):

    template_name = 'agenda/act-validation.html'

    def post(self, request, *args, **kwargs):
        return render_to_response(self.template_name, {},
                context_instance=None)

    def get_context_data(self, **kwargs):
        context = super(AgendaServiceActValidationView, self).get_context_data(**kwargs)
        day_locked = are_all_acts_of_the_day_locked(context['date'])
        authorized_lock = True # is_authorized_for_locking(get_request().user)
        validation_msg = list()
        acts_of_the_day = get_acts_of_the_day(context['date'])
        actes = list()
        for act in acts_of_the_day:
            state = act.get_state()
            if not state.previous_state:
                state = None
            act.date = act.date.strftime("%H:%M")
            actes.append((act, state))
        context['validation_states'] = VALIDATION_STATES
        context['actes'] = actes
        context['validation_msg'] = validation_msg
        context['day_locked'] = day_locked
        context['authorized_lock'] = authorized_lock
        return context


class AutomatedValidationView(CreateView):
    pass

class UnlockAllView(CreateView):
    pass
