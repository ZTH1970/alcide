# -*- coding: utf-8 -*-

import datetime

from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from calebasse.cbv import TemplateView, CreateView, UpdateView
from calebasse.agenda.models import Event, EventType, EventWithAct
from calebasse.personnes.models import TimeTable, Holiday
from calebasse.agenda.appointments import get_daily_appointments, get_daily_usage
from calebasse.personnes.models import Worker
from calebasse.ressources.models import WorkerType, Room
from calebasse.actes.validation import (get_acts_of_the_day,
        get_days_with_acts_not_locked)
from calebasse.actes.validation_states import VALIDATION_STATES
from calebasse.actes.models import Act, ValidationMessage
from calebasse.actes.validation import (automated_validation, unlock_all_acts_of_the_day)
from calebasse import cbv

from forms import (NewAppointmentForm, NewEventForm, UpdateAppointmentForm)

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

        context['workers_types'] = []
        workers = list(Worker.objects.filter(enabled=True).select_related())
        worker_by_type = {}
        for worker in workers:
            workers_for_type = worker_by_type.setdefault(worker.type, [])
            workers_for_type.append(worker)
        for worker_type, workers_for_type in worker_by_type.iteritems():
            context['workers_types'].append(
                    {'type': worker_type.name, 'workers': workers_for_type })
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
        plain_events = Event.objects.for_today(self.date) \
                .filter(services=self.service,
                        event_type__in=[appoinment_type, meeting_type])
        events = [ e.today_occurrence(self.date) for e in plain_events ]
        for event in events:
            start_datetime = event.start_datetime.strftime("%H:%M")
            if not appointments_times.has_key(start_datetime):
                appointments_times[start_datetime] = dict()
                appointments_times[start_datetime]['row'] = 0
                appointments_times[start_datetime]['appointments'] = []
            appointment = dict()
            length = event.end_datetime - event.start_datetime
            if length.seconds:
                length = length.seconds / 60
                appointment['length'] = "%sm" % length
            if event.event_type == EventType.objects.get(id=1):
                appointment['type'] = 1
                event_act = event.eventwithact
                appointment['label'] = event_act.patient.display_name
                appointment['act'] = event_act.act_type.name
            elif event.event_type == EventType.objects.get(id=2):
                appointment['type'] = 2
                appointment['label'] = '%s - %s' % (event.event_type.label,
                                                    event.title)
            else:
                appointment['type'] = 0
                appointment['label'] = '???'
            appointment['participants'] = event.participants.all()
            appointments_times[start_datetime]['row'] += 1
            appointments_times[start_datetime]['appointments'].append(appointment)
        context['appointments_times'] = sorted(appointments_times.items())
        return context


class NewAppointmentView(cbv.ReturnToObjectMixin, cbv.ServiceFormMixin, CreateView):
    model = EventWithAct
    form_class = NewAppointmentForm
    template_name = 'agenda/nouveau-rdv.html'
    success_url = '..'

    def get_initial(self):
        initial = super(NewAppointmentView, self).get_initial()
        initial['start_datetime'] = self.date
        initial['date'] = self.date
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        initial['room'] = self.request.GET.get('room')
        return initial

    def get_form_kwargs(self):
        kwargs = super(NewAppointmentView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs

class TodayOccurrenceMixin(object):
    def get_object(self, queryset=None):
        o = super(TodayOccurrenceMixin, self).get_object(queryset)
        return o.today_occurrence(self.date)

class UpdateAppointmentView(TodayOccurrenceMixin, UpdateView):
    model = EventWithAct
    form_class = UpdateAppointmentForm
    template_name = 'agenda/update-rdv.html'
    success_url = '..'

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()
        initial['start_datetime'] = self.date
        initial['date'] = self.object.start_datetime.date()
        initial['time'] = self.object.start_datetime.time()
        time = self.object.end_datetime - self.object.start_datetime
        if time:
            time = time.seconds / 60
        else:
            time = 0
        initial['duration'] = time
        initial['participants'] = self.object.participants.values_list('id', flat=True)
        return initial

    def get_form_kwargs(self):
        kwargs = super(UpdateAppointmentView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs


class NewEventView(CreateView):
    model = Event
    form_class = NewEventForm
    template_name = 'agenda/new-event.html'
    success_url = '..'

    def get_initial(self):
        initial = super(NewEventView, self).get_initial()
        initial['start_datetime'] = self.date
        initial['date'] = self.date
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        initial['event_type'] = 2
        initial['room'] = self.request.GET.get('room')
        return initial

    def get_form_kwargs(self):
        kwargs = super(NewEventView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs


class UpdateEventView(TodayOccurrenceMixin, UpdateView):
    model = Event
    form_class = NewEventForm
    template_name = 'agenda/update-event.html'
    success_url = '..'

    def get_initial(self):
        initial = super(UpdateEventView, self).get_initial()
        initial['start_datetime'] = self.date
        initial['date'] = self.object.start_datetime.date()
        initial['time'] = self.object.start_datetime.time()
        time = self.object.end_datetime - self.object.start_datetime
        if time:
            time = time.seconds / 60
        else:
            time = 0
        initial['duration'] = time
        initial['participants'] = self.object.participants.values_list('id', flat=True)
        return initial

    def get_form_kwargs(self):
        kwargs = super(UpdateEventView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs


class AgendaServiceActValidationView(TemplateView):
    template_name = 'agenda/act-validation.html'

    def acts_of_the_day(self):
        return [e.act for e in EventWithAct.objects.filter(patient__service=self.service)
                .today_occurrences(self.date)]

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
        nb_acts_abs_non_exc, nb_acts_abs_exc, nb_acts_abs_inter, nb_acts_annul_nous,
        nb_acts_annul_famille, nb_acts_reporte, nb_acts_abs_ess_pps,
        nb_acts_enf_hosp, nb_acts_losts) = \
            automated_validation(self.date, self.service,
                request.user, commit = False)

        nb_acts_not_validated = nb_acts_double + \
            nb_acts_abs_non_exc + \
            nb_acts_abs_exc + \
            nb_acts_abs_inter + \
            nb_acts_annul_nous + \
            nb_acts_annul_famille + \
            nb_acts_reporte + \
            nb_acts_abs_ess_pps + \
            nb_acts_enf_hosp + \
            nb_acts_losts
        context.update({
            'nb_acts_total': nb_acts_total,
            'nb_acts_validated': nb_acts_validated,
            'nb_acts_not_validated': nb_acts_not_validated,
            'nb_acts_double': nb_acts_double,
            'nb_acts_abs_non_exc': nb_acts_abs_non_exc,
            'nb_acts_abs_exc': nb_acts_abs_exc,
            'nb_acts_abs_inter': nb_acts_abs_inter,
            'nb_acts_annul_nous': nb_acts_annul_nous,
            'nb_acts_annul_famille': nb_acts_annul_famille,
            'nb_acts_reporte': nb_acts_reporte,
            'nb_acts_abs_ess_pps': nb_acts_abs_ess_pps,
            'nb_acts_enf_hosp': nb_acts_enf_hosp,
            'nb_acts_losts': nb_acts_losts})
        return context

class UnlockAllView(CreateView):
    pass


class AgendasTherapeutesView(AgendaHomepageView):
    template_name = 'agenda/agendas-therapeutes.html'

    def get_context_data(self, **kwargs):
        context = super(AgendasTherapeutesView, self).get_context_data(**kwargs)

        time_tables = TimeTable.objects.select_related('worker'). \
                filter(services=self.service). \
                for_today(self.date). \
                order_by('start_date')
        holidays = Holiday.objects.select_related('worker'). \
                for_period(self.date, self.date). \
                order_by('start_date')
        plain_events = Event.objects.for_today(self.date) \
                .filter(services=self.service) \
                .order_by('start_datetime').select_subclasses()
        events = [ e.today_occurrence(self.date) for e in plain_events ]

        events_workers = {}
        time_tables_workers = {}
        holidays_workers = {}
        context['workers_agenda'] = []
        for worker in context['workers']:
            time_tables_worker = [tt for tt in time_tables if tt.worker.id == worker.id]
            events_worker = [o for o in events if worker.id in o.participants.values_list('id', flat=True)]
            holidays_worker = [h for h in holidays if h.worker_id in (None, worker.id)]
            events_workers[worker.id] = events_worker
            time_tables_workers[worker.id] = time_tables_worker
            holidays_workers[worker.id] = holidays_worker
            context['workers_agenda'].append({'worker': worker,
                    'appointments': get_daily_appointments(context['date'], worker, self.service,
                        time_tables_worker, events_worker, holidays_worker)})

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
        acts = Act.objects.filter(is_billed=False,
            patient__service=self.service).order_by('date')
        days = set(acts.values_list('date', flat=True))
        if days:
            max_day, min_day = max(days), min(days)
            today = datetime.datetime.today().date()
            if max_day > today:
                max_day = today
            days &= set(get_days_with_acts_not_locked(min_day, max_day, self.service))
        context['days_not_locked'] = days
        return context

class RessourcesView(TemplateView):

    template_name = 'agenda/ressources.html'

    def get_context_data(self, **kwargs):
        context = super(RessourcesView, self).get_context_data(**kwargs)

        plain_events = Event.objects.for_today(self.date) \
                .order_by('start_datetime').select_subclasses()
        events = [ e.today_occurrence(self.date) for e in plain_events ]

        context['ressources_types'] = []
        context['ressources_agenda'] = []
        context['disponibility'] = {}
        ressources = []
        data = {'type': Room._meta.verbose_name_plural, 'ressources': Room.objects.all() }
        context['ressources_types'].append(data)
        ressources.extend(data['ressources'])

        events_ressources = {}
        for ressource in ressources:
            events_ressource = [e for e in events if ressource == e.room]
            events_ressources[ressource.id] = events_ressource
            context['ressources_agenda'].append({'ressource': ressource,
                    'appointments': get_daily_usage(context['date'], ressource,
                        self.service, events_ressource)})

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
        plain_events = Event.objects.for_today(self.date) \
                .order_by('start_datetime').select_subclasses()
        events = [ e.today_occurrence(self.date) for e in plain_events ]
        events_worker = [e for e in events if worker_id in e.participants.values_list('id', flat=True)]

        worker = Worker.objects.get(pk=worker_id)
        context['worker_agenda'] = {'worker': worker,
                    'appointments': get_daily_appointments(context['date'], worker, self.service,
                        time_tables_worker, events_worker, holidays_worker)}
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
        events = Event.objects.today_occurrences(self.date)
        events_worker = [e for e in events if worker_id in e.participants.values_list('id', flat=True)]

        worker = Worker.objects.get(pk=worker_id)
        time_tables_workers = {worker.id: time_tables_worker}
        events_workers = {worker.id: events_worker}
        holidays_workers = {worker.id: holidays_worker}

        context['initials'] = worker.get_initials()
        context['worker_id'] = worker.id
        context['disponibility'] = Event.objects.daily_disponibilities(self.date,
                events_workers, [worker], time_tables_workers, holidays_workers)
        return context
