# -*- coding: utf-8 -*-

from datetime import datetime, time
from datetime import time as datetime_time

from interval import Interval, IntervalSet

from calebasse.actes.validation_states import VALIDATION_STATES
from .models import EventWithAct

class Appointment(object):

    def __init__(self, title=None, begin_time=None, type=None,
            length=None, description=None, ressource=None):
        self.title = title
        self.type = type
        self.length = length
        self.description = description
        self.ressource = ressource
        self.is_recurrent = False
        self.is_billed = False
        self.convocation_sent = None
        self.other_services_names = []
        self.patient = None
        self.patient_record_id = None
        self.patient_record_paper_id = None
        self.event_id = None
        self.event_type = None
        self.workers = None
        self.workers_initial = None
        self.workers_codes = None
        self.act_id = None
        self.act_state = None
        self.act_absence = None
        self.weight = 0
        self.act_type = None
        self.validation = None
        self.holiday = False
        self.services_names = []
        self.event = False
        self.__set_time(begin_time)

    def __set_time(self, time):
        self.begin_time = time
        if time:
            self.begin_hour = time.strftime("%H:%M")
        else:
            self.begin_hour = None

    def init_from_event(self, event, service, validation_states=None):
        delta = event.end_datetime - event.start_datetime
        self.event = isinstance(event, EventWithAct)
        self.event_id = event.id
        self.length = delta.seconds / 60
        self.title = event.title
        if (hasattr(event, 'parent') and event.parent.recurrence_periodicity) or \
                event.exception_to:
            self.is_recurrent = True
        services = event.services.all()
        self.date = event.start_datetime.date()
        self.__set_time(time(event.start_datetime.hour, event.start_datetime.minute))
        for e_service in services:
            name = e_service.name.lower().replace(' ', '-')
            if e_service != service:
                self.other_services_names.append(name)
            self.services_names.append(name)
        if service in services:
            self.type = "busy-here"
        else:
            self.type = "busy-elsewhere"
        self.event_id = event.id
        if event.ressource:
            self.ressource = event.ressource.name
        self.description = event.description
        self.workers_initial = ""
        self.workers_code = []
        self.workers = event.participants.all()
        self.len_workers = event.participants.count()
        self.workers_absent = event.get_missing_participants()
        if event.event_type.id == 1:
            self.act_id = event.act.id
            self.convocation_sent = event.convocation_sent
            self.patient = event.patient
            self.patient_record_id = event.patient.id
            self.patient_record_paper_id = event.patient.paper_id
            self.act_type = event.act_type.name
            if self.act_id:
                self.description = event.act.comment
            self.is_billed = event.act.is_billed
            state = event.get_state()
            state_name = state.state_name if state else 'NON_VALIDE'
            display_name = VALIDATION_STATES[state_name]
            if event.is_absent():
                self.act_absence = VALIDATION_STATES.get(state_name)
            if state and not state.previous_state and state.state_name == 'NON_VALIDE':
                state = None
            if not service in services:
                validation_states = None
            self.validation = (event.act, state, display_name, validation_states)
            self.title = event.patient.display_name
        else:
            if event.event_type.label == 'Autre' and event.title:
                self.title = event.title
            else:
                self.title = '%s' % event.event_type.label
                if event.title:
                    self.title += ' - %s' % event.title
            self.event_type = event.event_type
        for worker in self.workers:
            self.workers_code.append("%s-%s" % (worker.id, worker.last_name.upper()))
        if not self.description:
            self.description = ''

    def init_free_time(self, length, begin_time):
        self.type = "free"
        self.length = length
        self.__set_time(begin_time)

    def init_busy_time(self, title, length, begin_time, description=None):
        self.title = title
        self.length = length
        self.__set_time(begin_time)
        self.description = description

    def init_holiday_time(self, title, length, begin_time, description=None):
        self.init_busy_time(title, length, begin_time, description)
        self.holiday = True

    def init_start_stop(self, title, time):
        """
        title: Arrivee ou Depart
        """
        self.type = "info"
        self.title = title
        self.__set_time(time)

def get_daily_appointments(date, worker, service, time_tables, events, holidays):
    """
    """
    appointments = []

    timetables_set = IntervalSet((t.to_interval(date) for t in time_tables))
    holidays_set = IntervalSet((h.to_interval(date) for h in holidays))
    busy_occurrences_set = IntervalSet((o.to_interval() for o in events if not o.is_event_absence()))
    for free_time in timetables_set - (busy_occurrences_set+holidays_set):
        if free_time:
            delta = free_time.upper_bound - free_time.lower_bound
            delta_minutes = delta.seconds / 60
            appointment = Appointment()
            appointment.init_free_time(delta_minutes,
                    time(free_time.lower_bound.hour, free_time.lower_bound.minute))
            appointments.append(appointment)
    validation_states = dict(VALIDATION_STATES)
    if service.name != 'CMPP' and \
            'ACT_DOUBLE' in validation_states:
        validation_states.pop('ACT_DOUBLE')
    vs = [('VALIDE', 'Présent')]
    validation_states.pop('VALIDE')
    validation_states.pop('ACT_LOST')
    validation_states = vs + sorted(validation_states.items(), key=lambda tup: tup[0])
    for event in events:
        appointment = Appointment()
        appointment.init_from_event(event, service, validation_states)
        appointments.append(appointment)
    for holiday in holidays:
        interval = holiday.to_interval(date)
        delta = interval.upper_bound - interval.lower_bound
        delta_minutes = delta.seconds / 60
        appointment = Appointment()
        appointment.type = 'busy-here'
        label = None
        if not holiday.worker:
            label = u"Absence de groupe : %s" % holiday.holiday_type.name
        else:
            label = u"Absence indiv. : %s" % holiday.holiday_type.name
        appointment.init_holiday_time(label,
                    delta_minutes,
                    time(interval.lower_bound.hour, interval.lower_bound.minute),
                    description=holiday.comment)
        services = holiday.services.all()
        if service not in services:
            appointment.type = 'busy-elsewhere'
        appointment.other_services_names = [s.slug for s in services if s != service]
        appointments.append(appointment)
    for time_table in time_tables:
        interval_set = IntervalSet.between(time_table.to_interval(date).lower_bound.time(),
                                   time_table.to_interval(date).upper_bound.time())
        for holiday in holidays:
            holiday_interval_set = IntervalSet.between(holiday.to_interval(date).lower_bound.time(),
                                   holiday.to_interval(date).upper_bound.time())
            interval_set = interval_set - holiday_interval_set
        if not interval_set:
            continue
        start_time = interval_set.lower_bound()
        end_time = interval_set.upper_bound()
        appointment = Appointment()
        appointment.init_start_stop(u"Arrivée", start_time)
        appointment.weight = -1
        appointments.append(appointment)
        appointment = Appointment()
        appointment.init_start_stop(u"Départ", end_time)
        appointment.weight = 1
        appointments.append(appointment)

    return sorted(appointments, key=lambda app: (app.begin_time, app.weight, app.event_id))

def get_daily_usage(date, ressource, service, occurrences):
    """
    """
    appointments = []

    start_time = datetime_time(8, 0)
    end_time = datetime_time(20, 0)
    all_day = Interval(datetime.combine(date, start_time), datetime.combine(date, end_time))
    timetables_set = IntervalSet([all_day])
    occurrences_set = IntervalSet((o.to_interval() for o in occurrences))
    for free_time in timetables_set - occurrences_set:
        if free_time:
            delta = free_time.upper_bound - free_time.lower_bound
            delta_minutes = delta.seconds / 60
            appointment = Appointment()
            appointment.init_free_time(delta_minutes,
                    time(free_time.lower_bound.hour, free_time.lower_bound.minute))
            appointments.append(appointment)
    for occurrence in occurrences:
        appointment = Appointment()
        appointment.init_from_event(occurrence, service)
        appointments.append(appointment)

    return sorted(appointments, key=lambda app: (app.begin_time, app.weight))
