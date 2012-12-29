# -*- coding: utf-8 -*-

import datetime

from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from calebasse.cbv import TemplateView, CreateView, UpdateView
from calebasse.agenda.models import Occurrence, Event, EventType
from calebasse.personnes.models import TimeTable, Holiday
from calebasse.actes.models import EventAct
from calebasse.agenda.appointments import get_daily_appointments, get_daily_usage
from calebasse.personnes.models import Worker
from calebasse.ressources.models import WorkerType, Room
from calebasse.actes.validation import get_acts_of_the_day
from calebasse.actes.validation_states import VALIDATION_STATES
from calebasse.actes.models import Act, ValidationMessage
from calebasse.actes.validation import (automated_validation,
    unlock_all_acts_of_the_day, are_all_acts_of_the_day_locked)
from calebasse import cbv

from forms import (NewAppointmentForm, NewEventForm,
        UpdateAppointmentForm, UpdateEventForm)

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect('agenda', date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)

class AgendaHomepageView(TemplateView):

    template_name = 'agenda/index.html'

    def post(self, request, *args, **kwargs):
        acte_id = request.POST.get('acte-id')
        try:
            act = Act.objects.get(id=acte_id)
            if not act.validation_locked:
                state_name = request.POST.get('act_state')
                act.set_state(state_name, request.user)
        except Act.DoesNotExist:
            pass
        return HttpResponseRedirect('#acte-frame-'+acte_id)

    def get_context_data(self, **kwargs):
        context = super(AgendaHomepageView, self).get_context_data(**kwargs)

        time_tables = TimeTable.objects.select_related('worker'). \
                filter(services=self.service). \
                for_today(self.date). \
                order_by('start_date')
        holidays = Holiday.objects.select_related('worker'). \
                for_period(self.date, self.date). \
                order_by('start_date')
        occurrences = Occurrence.objects.daily_occurrences(context['date']).order_by('start_time')

        context['time_tables'] = time_tables
        context['holidays'] = holidays
        context['occurrences'] = occurrences

        context['workers_types'] = []
        context['workers_agenda'] = []
        context['disponibility'] = {}
        workers = []
        for worker_type in WorkerType.objects.all():
            workers_type = Worker.objects.filter(enabled=True, type=worker_type)
            if workers_type:
                data = {'type': worker_type.name, 'workers': workers_type }
                context['workers_types'].append(data)
                workers.extend(data['workers'])

        context['workers'] = workers
        context['disponibility_start_times'] = range(8, 20)
        return context

class AgendaServiceActivityView(TemplateView):

    template_name = 'agenda/service-activity.html'

    def get_context_data(self, **kwargs):
        context = super(AgendaServiceActivityView, self).get_context_data(**kwargs)

        appointments_times = dict()
        appoinment_type = EventType.objects.get(id=1)
        meeting_type = EventType.objects.get(id=2)
        occurrences = Occurrence.objects.daily_occurrences(context['date'],
                services=[self.service],
                event_type=[appoinment_type, meeting_type])
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
            if occurrence.event.event_type == EventType.objects.get(id=1):
                appointment['type'] = 1
                event_act = occurrence.event.eventact
                appointment['label'] = event_act.patient.display_name
                appointment['act'] = event_act.act_type.name
            elif occurrence.event.event_type == EventType.objects.get(id=2):
                appointment['type'] = 2
                appointment['label'] = '%s - %s' % (occurrence.event.event_type.label,
                                                    occurrence.event.title)
            else:
                appointment['type'] = 0
                appointment['label'] = '???'
            appointment['participants'] = occurrence.event.participants.all()
            appointments_times[start_time]['row'] += 1
            appointments_times[start_time]['appointments'].append(appointment)
        context['appointments_times'] = sorted(appointments_times.items())
        return context


class NewAppointmentView(cbv.ReturnToObjectMixin, cbv.ServiceFormMixin, CreateView):
    model = EventAct
    form_class = NewAppointmentForm
    template_name = 'agenda/nouveau-rdv.html'
    success_url = '..'

    def get_initial(self):
        initial = super(NewAppointmentView, self).get_initial()
        initial['date'] = self.date
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        initial['room'] = self.request.GET.get('room')
        return initial


class UpdateAppointmentView(UpdateView):
    model = EventAct
    form_class = UpdateAppointmentForm
    template_name = 'agenda/update-rdv.html'
    success_url = '..'

    def get_object(self, queryset=None):
        self.occurrence = Occurrence.objects.get(id=self.kwargs['id'])
        if self.occurrence.event.eventact:
            return self.occurrence.event.eventact

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()
        initial['date'] = self.object.date
        initial['time'] = self.occurrence.start_time.strftime("%H:%M")
        time = self.occurrence.end_time - self.occurrence.start_time
        if time:
            time = time.seconds / 60
        else:
            time = 0
        initial['duration'] = time
        initial['participants'] = self.object.participants.values_list('id', flat=True)
        return initial

    def get_form_kwargs(self):
        kwargs = super(UpdateAppointmentView, self).get_form_kwargs()
        kwargs['occurrence'] = self.occurrence
        kwargs['service'] = self.service
        return kwargs


class NewEventView(CreateView):
    model = Event
    form_class = NewEventForm
    template_name = 'agenda/new-event.html'
    success_url = '..'

    def get_initial(self):
        initial = super(NewEventView, self).get_initial()
        initial['date'] = self.date
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        initial['services'] = [self.service]
        initial['event_type'] = 2
        initial['room'] = self.request.GET.get('room')
        return initial

class UpdateEventView(UpdateView):
    model = Event
    form_class = UpdateEventForm
    template_name = 'agenda/update-event.html'
    success_url = '..'

    def get_object(self, queryset=None):
        self.occurrence = Occurrence.objects.get(id=self.kwargs['id'])
        return self.occurrence.event

    def get_initial(self):
        initial = super(UpdateEventView, self).get_initial()
        initial['date'] = self.occurrence.start_time.date()
        initial['time'] = self.occurrence.start_time.strftime("%H:%M")
        time = self.occurrence.end_time - self.occurrence.start_time
        if time:
            time = time.seconds / 60
        else:
            time = 0
        initial['duration'] = time
        initial['participants'] = self.object.participants.values_list('id', flat=True)
        return initial

    def get_form_kwargs(self):
        kwargs = super(UpdateEventView, self).get_form_kwargs()
        kwargs['occurrence'] = self.occurrence
        return kwargs

def new_appointment(request):
    pass

class AgendaServiceActValidationView(TemplateView):

    template_name = 'agenda/act-validation.html'

    def acts_of_the_day(self):
        return get_acts_of_the_day(self.date, self.service)

    def post(self, request, *args, **kwargs):
        if 'unlock-all' in request.POST:
            #TODO: check that the user is authorized
            unlock_all_acts_of_the_day(self.date, self.service)
            ValidationMessage(validation_date=self.date,
                who=request.user, what='Déverrouillage',
                service=self.service).save()
        else:
            acte_id = request.POST.get('acte-id')
            try:
                act = Act.objects.get(id=acte_id)
                if 'lock' in request.POST or 'unlock' in request.POST:
                    #TODO: check that the user is authorized
                    act.validation_locked = 'lock' in request.POST
                    act.save()
                else:
                    state_name = request.POST.get('act_state')
                    act.set_state(state_name, request.user)
            except Act.DoesNotExist:
                pass
            return HttpResponseRedirect('#acte-frame-'+acte_id)
        return HttpResponseRedirect('')

    def get_context_data(self, **kwargs):
        context = super(AgendaServiceActValidationView, self).get_context_data(**kwargs)
        authorized_lock = True # is_authorized_for_locking(get_request().user)
        validation_msg = ValidationMessage.objects.\
            filter(validation_date=self.date, service=self.service).\
            order_by('-when')[:3]
        acts_of_the_day = self.acts_of_the_day()
        actes = list()
        for act in acts_of_the_day:
            state = act.get_state()
            display_name = VALIDATION_STATES[state.state_name]
            if not state.previous_state:
                state = None
            act.date = act.date.strftime("%H:%M")
            actes.append((act, state, display_name))
        context['validation_states'] = dict(VALIDATION_STATES)
        if self.service.name != 'CMPP' and \
                'ACT_DOUBLE' in context['validation_states']:
            context['validation_states'].pop('ACT_DOUBLE')
        context['actes'] = actes
        context['validation_msg'] = validation_msg
        context['authorized_lock'] = authorized_lock
        return context


class AutomatedValidationView(TemplateView):
    template_name = 'agenda/automated-validation.html'

    def post(self, request, *args, **kwargs):
        automated_validation(self.date, self.service,
            request.user)
        ValidationMessage(validation_date=self.date,
            who=request.user, what='Validation automatique',
            service=self.service).save()
        return HttpResponseRedirect('..')

    def get_context_data(self, **kwargs):
        context = super(AutomatedValidationView, self).get_context_data(**kwargs)
        request = self.request
        (nb_acts_total, nb_acts_validated, nb_acts_double,
            nb_acts_abs_non_exc, nb_acts_abs_exc, nb_acts_annul_nous,
            nb_acts_annul_famille, nb_acts_reporte, nb_acts_abs_ess_pps,
            nb_acts_enf_hosp) = \
            automated_validation(self.date, self.service,
                request.user, commit = False)

        nb_acts_not_validated = nb_acts_double + \
            nb_acts_abs_non_exc + \
            nb_acts_abs_exc + \
            nb_acts_annul_nous + \
            nb_acts_annul_famille + \
            nb_acts_reporte + \
            nb_acts_abs_ess_pps + \
            nb_acts_enf_hosp
        context.update({
            'nb_acts_total': nb_acts_total,
            'nb_acts_validated': nb_acts_validated,
            'nb_acts_not_validated': nb_acts_not_validated,
            'nb_acts_double': nb_acts_double,
            'nb_acts_abs_non_exc': nb_acts_abs_non_exc,
            'nb_acts_abs_exc': nb_acts_abs_exc,
            'nb_acts_annul_nous': nb_acts_annul_nous,
            'nb_acts_annul_famille': nb_acts_annul_famille,
            'nb_acts_reporte': nb_acts_reporte,
            'nb_acts_abs_ess_pps': nb_acts_abs_ess_pps,
            'nb_acts_enf_hosp': nb_acts_enf_hosp})
        return context

class UnlockAllView(CreateView):
    pass


class AgendasTherapeutesView(AgendaHomepageView):

    template_name = 'agenda/agendas-therapeutes.html'

    def get_context_data(self, **kwargs):
        context = super(AgendasTherapeutesView, self).get_context_data(**kwargs)
        time_tables = context['time_tables']
        holidays = context['holidays']
        occurrences = context['occurrences']
        occurrences_workers = {}
        time_tables_workers = {}
        holidays_workers = {}
        context['workers_agenda'] = []
        for worker in context['workers']:
            time_tables_worker = [tt for tt in time_tables if tt.worker.id == worker.id]
            occurrences_worker = [o for o in occurrences if worker.id in o.event.participants.values_list('id', flat=True)]
            holidays_worker = [h for h in holidays if h.worker_id in (None, worker.id)]
            occurrences_workers[worker.id] = occurrences_worker
            time_tables_workers[worker.id] = time_tables_worker
            holidays_workers[worker.id] = holidays_worker
            context['workers_agenda'].append({'worker': worker,
                    'appointments': get_daily_appointments(context['date'], worker, self.service,
                        time_tables_worker, occurrences_worker, holidays_worker)})

        for worker_agenda in context.get('workers_agenda', []):
            patient_appointments = [x for x in worker_agenda['appointments'] if x.patient_record_id]
            worker_agenda['summary'] = {
              'rdv': len(patient_appointments),
              'presence': len([x for x in patient_appointments if x.act_absence is None]),
              'absence': len([x for x in patient_appointments if x.act_absence is not None]),
              'doubles': len([x for x in patient_appointments if x.act_type == 'ACT_DOUBLE']),
              'valides': len([x for x in patient_appointments if x.act_type == 'ACT_VALIDE']),
            }

        return context

class JoursNonVerrouillesView(TemplateView):

    template_name = 'agenda/days-not-locked.html'

    def get_context_data(self, **kwargs):
        context = super(JoursNonVerrouillesView, self).get_context_data(**kwargs)
        acts = EventAct.objects.filter(is_billed=False,
            patient__service=self.service).order_by('date')
        days_not_locked = []
        for act in acts:
            current_day = datetime.datetime(act.date.year, act.date.month, act.date.day)
            if not current_day in days_not_locked:
                locked = are_all_acts_of_the_day_locked(current_day, self.service)
                if not locked:
                    days_not_locked.append(current_day)
        context['days_not_locked'] = days_not_locked
        return context

class RessourcesView(TemplateView):

    template_name = 'agenda/ressources.html'

    def get_context_data(self, **kwargs):
        context = super(RessourcesView, self).get_context_data(**kwargs)

        occurrences = Occurrence.objects.daily_occurrences(context['date']).order_by('start_time')

        context['ressources_types'] = []
        context['ressources_agenda'] = []
        context['disponibility'] = {}
        ressources = []
        data = {'type': Room._meta.verbose_name_plural, 'ressources': Room.objects.all() }
        context['ressources_types'].append(data)
        ressources.extend(data['ressources'])

        occurrences_ressources = {}
        for ressource in ressources:
            occurrences_ressource = [o for o in occurrences if ressource == o.event.room]
            occurrences_ressources[ressource.id] = occurrences_ressource
            context['ressources_agenda'].append({'ressource': ressource,
                    'appointments': get_daily_usage(context['date'], ressource,
                        self.service, occurrences_ressource)})

        return context

class AjaxWorkerTabView(TemplateView):

    template_name = 'agenda/ajax-worker-tab.html'

    def get_context_data(self, worker_id, **kwargs):
        context = super(AjaxWorkerTabView, self).get_context_data(**kwargs)
        worker_id = int(worker_id)

        time_tables_worker = TimeTable.objects.select_related('worker'). \
                filter(services=self.service, worker_id=worker_id). \
                for_today(self.date). \
                order_by('start_date')
        holidays_worker = Holiday.objects.for_worker_id(worker_id). \
                for_period(self.date, self.date). \
                order_by('start_date')
        occurrences = Occurrence.objects.daily_occurrences(context['date']).order_by('start_time')
        occurrences_worker = [o for o in occurrences if worker_id in o.event.participants.values_list('id', flat=True)]

        worker = Worker.objects.get(pk=worker_id)
        context['worker_agenda'] = {'worker': worker,
                    'appointments': get_daily_appointments(context['date'], worker, self.service,
                        time_tables_worker, occurrences_worker, holidays_worker)}
        return context

class AjaxWorkerDisponibilityColumnView(TemplateView):

    template_name = 'agenda/ajax-worker-disponibility-column.html'

    def get_context_data(self, worker_id, **kwargs):
        context = super(AjaxWorkerDisponibilityColumnView, self).get_context_data(**kwargs)
        worker_id = int(worker_id)

        time_tables_worker = TimeTable.objects.select_related('worker'). \
                filter(services=self.service, worker_id=worker_id). \
                for_today(self.date). \
                order_by('start_date')
        holidays_worker = Holiday.objects.for_worker_id(worker_id). \
                for_period(self.date, self.date). \
                order_by('start_date')
        occurrences = Occurrence.objects.daily_occurrences(context['date']).order_by('start_time')
        occurrences_worker = [o for o in occurrences if worker_id in o.event.participants.values_list('id', flat=True)]

        worker = Worker.objects.get(pk=worker_id)
        time_tables_workers = {worker.id: time_tables_worker}
        occurrences_workers = {worker.id: occurrences_worker}
        holidays_workers = {worker.id: holidays_worker}

        context['disponibility'] = Occurrence.objects.daily_disponibility(context['date'],
                occurrences_workers, [worker], time_tables_workers, holidays_workers)
        return context
