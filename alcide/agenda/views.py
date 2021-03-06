# -*- coding: utf-8 -*-

import datetime
import logging
from itertools import chain

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings

from alcide.cbv import TemplateView, CreateView, UpdateView
from alcide.agenda.models import Event, EventType, EventWithAct
from alcide.personnes.models import TimeTable, Holiday
from alcide.agenda.appointments import get_daily_appointments, get_daily_usage
from alcide.personnes.models import Worker
from alcide.ressources.models import WorkerType, Ressource
from alcide.actes.validation import (get_acts_of_the_day,
        get_days_with_acts_not_locked)
from alcide.actes.validation_states import VALIDATION_STATES
from alcide.actes.models import Act, ValidationMessage
from alcide.actes.validation import (automated_validation, unlock_all_acts_of_the_day)
from alcide import cbv
from alcide.utils import get_service_setting

from alcide.agenda.forms import (NewAppointmentForm, NewEventForm, UpdatePeriodicAppointmentForm,
        DisablePatientAppointmentForm, UpdateAppointmentForm, UpdatePeriodicEventForm,
        UpdateEventForm, PeriodicEventsSearchForm)

logger = logging.getLogger(__name__)

def redirect_today(request, service):
    '''If not date is given we redirect on the agenda for today'''
    return redirect('agenda', date=datetime.date.today().strftime('%Y-%m-%d'),
            service=service)


class AgendaHomepageView(TemplateView):
    template_name = 'agenda/index.html'

    def post(self, request, *args, **kwargs):
        acte_id = request.POST.get('event-id')
        try:
            event = EventWithAct.objects.get(id=acte_id)
            event = event.today_occurrence(self.date)
            act = event.act
            if not act.validation_locked:
                state_name = request.POST.get('act_state')
                act.save()
                act.set_state(state_name, request.user)
        except Act.DoesNotExist:
            logger.warning('agenda homepage acte_id %d not found' % acte_id)
        return HttpResponseRedirect('#acte-frame-'+acte_id)

    def get_context_data(self, **kwargs):
        context = super(AgendaHomepageView, self).get_context_data(**kwargs)

        context['workers_types'] = []
        workers = Worker.objects.filter(enabled=True).select_related() \
                .prefetch_related('services')
        worker_by_type = {}
        for worker in workers:
            workers_for_type = worker_by_type.setdefault(worker.type, [])
            workers_for_type.append(worker)
        for worker_type, workers_for_type in worker_by_type.iteritems():
            context['workers_types'].append(
                    {'type': worker_type.name, 'workers': workers_for_type })
        context['workers'] = workers
        context['disponibility_start_times'] = range(8, 20)

        # ressources
        context['ressources_types'] = []
        data = {'type': Ressource._meta.verbose_name_plural,
                'ressources': Ressource.objects.all()}
        context['ressources_types'].append(data)

        return context

class AgendaServiceActivityView(TemplateView, cbv.ServiceViewMixin):
    template_name = 'agenda/service-activity.html'
    cookies_to_clear = [('agenda-tabs', ), ('active-agenda', ), ('last-ressource', )]

    def get_context_data(self, **kwargs):
        context = super(AgendaServiceActivityView, self).get_context_data(**kwargs)

        appointments_times = dict()
        events = Event.objects.for_today(self.date) \
                .exclude(event_type_id=1) \
                .filter(services=self.service) \
                .order_by('start_datetime', 'id') \
                .select_related() \
                .prefetch_related('participants', 'exceptions')
        eventswithact = EventWithAct.objects.for_today(self.date) \
                .filter(services=self.service) \
                .order_by('start_datetime', 'id') \
                .select_related() \
                .prefetch_related('participants', 'exceptions')
        events = [ e.today_occurrence(self.date) for e in events ] \
             + [ e.today_occurrence(self.date) for e in eventswithact ]
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
            if event.event_type_id == 1:
                appointment['type'] = 1
                appointment['label'] = event.patient.display_name
                appointment['paper_id'] = event.patient.paper_id
                appointment['act'] = event.act_type.name
                appointment['state'] = event.act.get_state()
                appointment['absent'] = event.act.is_absent()
            else:
                appointment['type'] = 2
                if event.event_type.label == 'Autre' and event.title:
                    appointment['label'] = event.title
                else:
                    appointment['label'] = '%s - %s' % (event.event_type.label,
                                                        event.title)
            appointment['participants'] = event.participants.filter(worker__enabled=True)
            appointment['len_participants'] = len(appointment['participants'])
            appointment['workers_absent'] = event.get_missing_participants()
            appointments_times[start_datetime]['row'] += 1
            appointments_times[start_datetime]['appointments'].append(appointment)
        context['appointments_times'] = sorted(appointments_times.items())
        return context


class NewAppointmentView(cbv.ServiceFormMixin, CreateView):
    model = EventWithAct
    form_class = NewAppointmentForm
    template_name = 'agenda/new-appointment.html'
    success_msg = u'Rendez-vous enregistré avec succès.'

    def get_initial(self):
        initial = super(NewAppointmentView, self).get_initial()
        initial['start_datetime'] = self.date
        initial['date'] = self.date
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        initial['ressource'] = self.request.GET.get('ressource')
        initial['duration'] = self.request.GET.get('duration')
        return initial

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '..')

    def form_valid(self, form):
        obj = super(NewAppointmentView, self).form_valid(form)
        messages.add_message(self.request, messages.INFO, self.success_msg)
        return obj


class TodayOccurrenceMixin(object):
    def get_object(self, queryset=None):
        o = super(TodayOccurrenceMixin, self).get_object(queryset)
        obj = o.today_occurrence(self.date)
        if obj:
            return obj
        raise Http404


class BaseAppointmentView(UpdateView):
    model = EventWithAct
    form_class = UpdateAppointmentForm
    template_name = 'agenda/update-rdv.html'
    success_url = '..'

    def get_initial(self):
        initial = super(BaseAppointmentView, self).get_initial()
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
        kwargs = super(BaseAppointmentView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs


class UpdateAppointmentView(TodayOccurrenceMixin, BaseAppointmentView):

    def get_form_class(self):
        if self.object.exception_to and not self.object.exception_to.canceled:
            return DisablePatientAppointmentForm
        else:
            return self.form_class

class UpdatePeriodicAppointmentView(BaseAppointmentView):
    form_class = UpdatePeriodicAppointmentForm
    template_name = 'agenda/new-appointment.html'

class NewEventView(CreateView):
    model = Event
    form_class = NewEventForm
    template_name = 'agenda/new-event.html'

    def get_initial(self):
        initial = super(NewEventView, self).get_initial()
        initial['start_datetime'] = self.date
        initial['date'] = self.date
        initial['participants'] = self.request.GET.getlist('participants')
        initial['time'] = self.request.GET.get('time')
        initial['event_type'] = 2
        initial['ressource'] = self.request.GET.get('ressource')
        initial['duration'] = self.request.GET.get('duration')
        if not initial.has_key('services'):
            initial['services'] = [self.service]
        return initial

    def get_form_kwargs(self):
        kwargs = super(NewEventView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '..')

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, u'Evénement enregistré avec succès.')
        return super(NewEventView, self).form_valid(form)

class BaseEventView(UpdateView):
    model = Event
    form_class = UpdateEventForm
    template_name = 'agenda/update-event.html'
    success_url = '..'

    def get_initial(self):
        initial = super(BaseEventView, self).get_initial()
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
        kwargs = super(BaseEventView, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs


class UpdateEventView(TodayOccurrenceMixin, BaseEventView):
    pass


class UpdatePeriodicEventView(BaseEventView):
    form_class = UpdatePeriodicEventForm
    template_name = 'agenda/new-event.html'

class DeleteOccurrenceView(TodayOccurrenceMixin, cbv.DeleteView):
    model = Event
    success_url = '..'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # If the exception does not exist we need to create it before set it canceled
        self.object.save()
        self.object.delete()
        return HttpResponse(status=204)

class DeleteEventView(cbv.DeleteView):
    model = Event
    success_url = '..'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse(status=204)

class AgendaServiceActValidationView(TemplateView):
    template_name = 'agenda/act-validation.html'
    cookies_to_clear = [('agenda-tabs', ), ('active-agenda', ), ('last-ressource', )]

    def acts_of_the_day(self):
        acts = list(Act.objects \
                .filter(date=self.date, patient__service=self.service) \
                .select_related() \
                .prefetch_related('doctors',
                        'patient__patientcontact',
                        'actvalidationstate_set__previous_state') \
                .order_by('time'))
        event_ids = [ a.parent_event_id for a in acts if a.parent_event_id ]
        events = EventWithAct.objects.for_today(self.date) \
                .filter(patient__service=self.service) \
                .exclude(id__in=event_ids)
        events = [ event.today_occurrence(self.date) for event in events ]
        acts += [ event.act for event in events if event ]
        return sorted(acts, key=lambda a: (a.time or datetime.time.min, a.id))

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
                    messages.add_message(self.request, messages.INFO, u'Acte modifié avec succès')
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
            if not act.id:
                if act.date < datetime.date(2013, 1, 1):
                    continue
                else:
                    act.save()
            state = act.get_state()
            display_name = None
            if state :
                display_name = VALIDATION_STATES[state.state_name]
                if not state.previous_state_id and state.state_name == 'NON_VALIDE':
                    state = None
            actes.append((act, state, display_name))
        validation_states = dict(VALIDATION_STATES)
        if self.service.name != 'CMPP' and \
                'ACT_DOUBLE' in validation_states:
            validation_states.pop('ACT_DOUBLE')
        vs = [('VALIDE', 'Présent')]
        validation_states.pop('VALIDE')
        validation_states.pop('ACT_LOST')
        validation_states = vs + sorted(validation_states.items(), key=lambda tup: tup[0])
        context['validation_states'] = validation_states
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
    cookies_to_clear = [('agenda-tabs', ), ('active-agenda', ), ('last-ressource', )]

    def get_context_data(self, **kwargs):
        context = super(AgendasTherapeutesView, self).get_context_data(**kwargs)
        current_service_only = settings.CURRENT_SERVICE_EVENTS_ONLY

        time_tables = TimeTable.objects.select_related('worker'). \
                filter(services=self.service). \
                for_today(self.date). \
                order_by('start_date')
        holidays = Holiday.objects.select_related('worker') \
                .for_period(self.date, self.date) \
                .order_by('start_date') \
                .select_related()
        events = Event.objects.for_today(self.date) \
                .exclude(event_type_id=1) \
                .order_by('start_datetime') \
                .select_related() \
                .prefetch_related('services',
                        'exceptions',
                        'participants')
        eventswithact = EventWithAct.objects.for_today(self.date) \
                .order_by('start_datetime') \
                .select_related() \
                .prefetch_related(
                        'services',
                        'patient__service',
                        'act_set__actvalidationstate_set',
                        'exceptions', 'participants')

        if current_service_only:
            events = events.filter(services=self.service)
            eventswithact = eventswithact.filter(services=self.service)

        context['CURRENT_SERVICE_EVENTS_ONLY'] = current_service_only

        events = [ e.today_occurrence(self.date) for e in events ] \
             + [ e.today_occurrence(self.date) for e in eventswithact ]
        for e in events:
            e.workers_ids = set(p.id for p in e.participants.all())

        events_workers = {}
        time_tables_workers = {}
        holidays_workers = {}
        context['workers_agenda'] = []
        context['workers'] = context['workers'].filter(services=self.service)
        for worker in context['workers']:
            time_tables_worker = [tt for tt in time_tables if tt.worker.id == worker.id]
            events_worker = [o for o in events if worker.id in o.workers_ids ]
            holidays_worker = [h for h in holidays if h.worker_id in (None, worker.id)]
            events_workers[worker.id] = events_worker
            time_tables_workers[worker.id] = time_tables_worker
            holidays_workers[worker.id] = holidays_worker
            activity, daily_appointments = get_daily_appointments(context['date'], worker, self.service,
                        time_tables_worker, events_worker, holidays_worker)
            if all(map(lambda x: x.holiday, daily_appointments)):
                continue

            context['workers_agenda'].append({'worker': worker,
                    'appointments': daily_appointments,
                    'activity': activity,
                    'has_events': True if events_worker else False})

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
        context['days_not_locked'] = sorted(days)
        return context

class AjaxWorkerTabView(TemplateView):

    template_name = 'agenda/ajax-worker-tab.html'

    def get_context_data(self, worker_id, **kwargs):
        context = super(AjaxWorkerTabView, self).get_context_data(**kwargs)
        worker = Worker.objects.get(id=worker_id)

        time_tables_worker = TimeTable.objects.select_related('worker'). \
                filter(worker=worker) \
                .for_today(self.date) \
                .order_by('start_date') \
                .select_related()

        holidays_worker = Holiday.objects.for_worker(worker) \
                .for_period(self.date, self.date) \
                .order_by('start_date') \
                .select_related()
        events = Event.objects.for_today(self.date) \
                .exclude(event_type_id=1) \
                .filter(participants=worker) \
                .order_by('start_datetime') \
                .select_related() \
                .prefetch_related('services',
                        'exceptions',
                        'participants')
        eventswithact = EventWithAct.objects.for_today(self.date) \
                .filter(participants=worker) \
                .order_by('start_datetime') \
                .select_related() \
                .prefetch_related('patient__addresses',
                        'patient__addresses__patientcontact_set',
                        'services',
                        'patient__service',
                        'act_set__actvalidationstate_set',
                        'exceptions', 'participants')
        events = [ e.today_occurrence(self.date) for e in events ] \
             + [ e.today_occurrence(self.date) for e in eventswithact ]
        activity, appointments = get_daily_appointments(context['date'], worker,
                                                        self.service, time_tables_worker,
                                                        events, holidays_worker)

        context['worker_agenda'] = {'worker': worker,
                                    'appointments': appointments}

        if settings.RTF_TEMPLATES_DIRECTORY:
            context['mail'] = True
        return context

class AjaxRessourceTabView(TemplateView):
    template_name = 'agenda/ajax-ressource-tab.html'

    def get_context_data(self, ressource_id, **kwargs):
        context = super(AjaxRessourceTabView, self).get_context_data(**kwargs)
        ressource = Ressource.objects.get(pk=ressource_id)
        plain_events = Event.objects.for_today(self.date) \
                                    .order_by('start_datetime').select_subclasses()
        events = [ e.today_occurrence(self.date) for e in plain_events ]
        events_ressource = [e for e in events if ressource == e.ressource]
        context['ressource_agenda'] = {'appointments': get_daily_usage(context['date'],
                                                                       ressource,
                                                                       self.service,
                                                                       events_ressource)
        }
        return context

class AjaxDisponibilityColumnView(TemplateView):

    template_name = 'agenda/ajax-disponibility-column.html'

    def get_ressource_context_data(self, ressource_id, context):
        ressource = Ressource.objects.get(pk = ressource_id)
        context['initials'] = ressource.name[:3]
        disponibility = dict()
        start_datetime = datetime.datetime(self.date.year,
                                           self.date.month,
                                           self.date.day, 8, 0)
        end_datetime = datetime.datetime(self.date.year, self.date.month,
                                         self.date.day, 8, 15)
        events = Event.objects.filter(ressource__id=ressource_id).today_occurrences(self.date)

        while (start_datetime.hour <= 19):
            if start_datetime.hour not in disponibility:
                disponibility[start_datetime.hour] = [[], [], [], []]
                quarter = 0
            dispo = 'free'
            mins = quarter * 15

            if events:
                for event in events:
                    if get_service_setting('show_overlapping_appointments'):
                        overlap_events = Event.objects.overlap_occurences(start_datetime, events)
                    else:
                        overlap_events = []
                    if len(overlap_events) > 1:
                        dispo = 'overlap'
                    elif event.start_datetime <= start_datetime and event.end_datetime >= end_datetime:
                        dispo = 'busy'
            disponibility[start_datetime.hour][quarter].append((mins, {'id': ressource_id, 'dispo': dispo}))
            quarter += 1
            start_datetime += datetime.timedelta(minutes=15)
            end_datetime += datetime.timedelta(minutes=15)

        context['disponibility'] = disponibility
        return context


    def get_worker_context_data(self, worker_id, context):
        worker = Worker.objects.get(pk=worker_id)

        time_tables = TimeTable.objects.select_related('worker'). \
                filter(services=self.service, worker=worker). \
                for_today(self.date). \
                order_by('start_date')
        holidays = Holiday.objects.for_worker(worker). \
                for_period(self.date, self.date). \
                order_by('start_date')
        events = Event.objects.for_today(self.date) \
                .exclude(event_type_id=1) \
                .filter(participants=worker) \
                .order_by('start_datetime') \
                .select_related() \
                .prefetch_related('participants', 'exceptions')
        eventswithact = EventWithAct.objects.for_today(self.date) \
                .filter(participants=worker) \
                .order_by('start_datetime') \
                .select_related() \
                .prefetch_related('participants', 'exceptions',
                        'act_set__actvalidationstate_set')

        events = list(events) + list(eventswithact)
        events = [ e.today_occurrence(self.date) for e in events ]
        time_tables_workers = {worker.id: time_tables}
        events_workers = {worker.id: events}
        holidays_workers = {worker.id: holidays}

        context['initials'] = worker.initials
        context['disponibility'] = Event.objects.daily_disponibilities(self.date,
                events, worker, time_tables, holidays)
        return context

    def get_context_data(self, ressource_type, ressource_id, **kwargs):
        context = super(AjaxDisponibilityColumnView, self).get_context_data(**kwargs)
        if ressource_type in ('worker', 'ressource',):
            context['ressource_type'] = ressource_type
            context['ressource_id'] = ressource_id
            getattr(self, 'get_%s_context_data' % ressource_type)(ressource_id, context)
        return context

class PeriodicEventsView(cbv.ListView):
    model = EventWithAct
    template_name = 'agenda/periodic-events.html'
    cookies_to_clear = [('agenda-tabs', ), ('active-agenda', ), ('last-ressource', )]

    def dispatch(self, request, *args, **kwargs):
        if 'worker_id' in kwargs:
            self.worker = get_object_or_404(Worker, id=kwargs['worker_id'])
        else:
            self.worker = None
        return super(PeriodicEventsView, self).dispatch(request, *args, **kwargs)

    def get_form(self):
        kwargs = {
                'initial': {
                    'start_date': self.date,
                }
        }
        if self.request.GET:
            kwargs['data'] = self.request.GET
        self.form = PeriodicEventsSearchForm(prefix='periodic-events-search-form', **kwargs)
        return self.form

    def get_queryset(self):
        qs1 = Event.objects.exclude(event_type_id=1)
        qs2 = EventWithAct.objects.all()
        form = self.get_form()
        if not self.request.GET:
            return ()
        qs1 = self.filter_queryset(form, qs1)
        qs2 = self.filter_queryset(form, qs2)
        if form.is_valid():
            patient = form.cleaned_data.get('patient')
            if patient is not None:
                qs1 = qs1.none()
                qs2 = qs2.filter(patient=patient)
            worker = form.cleaned_data.get('worker')
            if worker is not None:
                qs1 = qs1.filter(participants=worker)
                qs2 = qs2.filter(participants=worker)
        return sorted(chain(qs1, qs2),
                key=lambda x: (x.start_datetime, x.recurrence_end_date or datetime.date(9999,12,31)))

    def filter_queryset(self, form, qs):
        if self.worker is not None:
            qs = qs.filter(participants=self.worker)
        start_date = datetime.date.today()
        end_date = start_date+datetime.timedelta(days=90)
        if form.is_valid():
            if form.cleaned_data.get('start_date'):
                start_date = form.cleaned_data['start_date']
            if form.cleaned_data.get('end_date'):
                end_date = form.cleaned_data['end_date']
            else:
                end_date = start_date+datetime.timedelta(days=90)
            if len(form.cleaned_data.get('event_type')) != 2:
                if '0' in form.cleaned_data.get('event_type'):
                    qs = qs.filter(event_type_id=1)
                else:
                    qs = qs.exclude(event_type_id=1)
            if form.cleaned_data.get('no_end_date'):
                qs = qs.filter(recurrence_end_date__isnull=True)
        qs = qs.filter(canceled=False)
        qs = qs.filter(services=self.service)
        qs = qs.filter(recurrence_periodicity__isnull=False)
        qs = qs.filter(start_datetime__lt=end_date)
        qs = qs.filter(Q(recurrence_end_date__isnull=True)
                | Q(recurrence_end_date__gte=start_date))
        qs = qs.order_by('start_datetime', 'recurrence_end_date')
        qs = qs.select_related()
        qs = qs.prefetch_related('participants', 'services')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(PeriodicEventsView, self).get_context_data(**kwargs)
        ctx['search_form'] = self.form
        ctx['worker'] = self.worker
        return ctx
