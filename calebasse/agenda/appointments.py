# -*- coding: utf-8 -*-

from datetime import datetime, time
from datetime import time as datetime_time

from interval import Interval, IntervalSet

from calebasse.actes.validation_states import VALIDATION_STATES

class Appointment(object):

    def __init__(self, title=None, begin_time=None, type=None,
            length=None, description=None, room=None):
        """ """
        self.title = title
        self.type = type
        self.length = length
        self.description = description
        self.room = room
        self.is_recurrent = False
        self.convocation_sent = None
        self.other_services_names = []
        self.patient_record_id = None
        self.patient_record_paper_id = None
        self.event_id = None
        self.event_type = None
        self.workers = None
        self.workers_initial = None
        self.workers_codes = None
        self.act_state = None
        self.act_absence = None
        self.weight = 0
        self.act_type = None
        self.validation = None
        self.__set_time(begin_time)

    def __set_time(self, time):
        self.begin_time = time
        if time:
            self.begin_hour = time.strftime("%H:%M")
        else:
            self.begin_hour = None

    def __get_initials(self, personns):
        pass

    def init_from_event(self, event, service, validation_states=None):
        """ """
        delta = event.end_datetime - event.start_datetime
        self.event_id = event.id
        self.length = delta.seconds / 60
        self.title = event.title
        if hasattr(event, 'parent') and event.parent.recurrence_periodicity:
            self.is_recurrent = True
        services = event.services.all()
        self.date = event.start_datetime.date()
        self.__set_time(time(event.start_datetime.hour, event.start_datetime.minute))
        for e_service in services:
            if e_service != service:
                name = e_service.name.lower().replace(' ', '-')
                self.other_services_names.append(name)
        if service in services:
            self.type = "busy-here"
        else:
            self.type = "busy-elsewhere"
        self.event_id = event.id
        if event.room:
            self.room = event.room.name
        self.description = event.description
        self.workers_initial = ""
        self.workers_code = []
        if event.event_type.id == 1:
            self.workers = event.participants.all()
            self.convocation_sent = event.convocation_sent
            self.patient = event.patient
            self.patient_record_id = event.patient.id
            self.patient_record_paper_id = event.patient.paper_id
            self.act_type = event.act_type.name
            self.act_state = event.act.get_state().state_name
            if self.act_state not in ('NON_VALIDE', 'VALIDE', 'ACT_DOUBLE'):
                self.act_absence = VALIDATION_STATES.get(self.act_state)
            state = event.act.get_state()
            display_name = VALIDATION_STATES[state.state_name]
            if not state.previous_state and state.state_name == 'NON_VALIDE':
                state = None
            if not service in services:
                validation_states = None
            self.validation = (event.act, state, display_name, validation_states)
        else:
            self.event_type = event.event_type
            self.workers = event.participants.all()
        for worker in self.workers:
            self.workers_initial += " " + worker.get_initials()
            self.workers_code.append("%s-%s" % (worker.id, worker.last_name.upper()))

    def init_free_time(self, length, begin_time):
        """ """
        self.type = "free"
        self.length = length
        self.__set_time(begin_time)

    def init_busy_time(self, title, length, begin_time, description=None):
        self.title = title
        self.type = "busy-here"
        self.length = length
        self.__set_time(begin_time)
        self.description = description

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
        label = u"Congé (%s)" % holiday.holiday_type.name
        appointment.init_busy_time(label,
                    delta_minutes,
                    time(interval.lower_bound.hour, interval.lower_bound.minute),
                    description=holiday.comment)
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

    return sorted(appointments, key=lambda app: (app.begin_time, app.weight))

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
        appointment.init_from_occurrence(occurrence, service)
        appointments.append(appointment)

    return sorted(appointments, key=lambda app: (app.begin_time, app.weight))
