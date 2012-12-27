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
        self.convocation_sent = None
        self.other_services_names = []
        self.patient_record_id = None
        self.patient_record_paper_id = None
        self.event_id = None
        self.event_type = None
        self.occurrence_id = None
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

    def init_from_occurrence(self, occurrence, service):
        """ """
        delta = occurrence.end_time - occurrence.start_time
        self.occurrence_id = occurrence.id
        self.length = delta.seconds / 60
        self.title = occurrence.title
        services = occurrence.event.services.all()
        self.date = occurrence.start_time.date()
        self.__set_time(time(occurrence.start_time.hour, occurrence.start_time.minute))
        for e_service in services:
            if e_service != service:
                name = e_service.name.lower().replace(' ', '-')
                self.other_services_names.append(name)
        if service in services:
            self.type = "busy-here"
        else:
            self.type = "busy-elsewhere"
        self.event_id = occurrence.event.id
        if occurrence.event.room:
            self.room = occurrence.event.room.name
        self.description = occurrence.event.description
        if occurrence.event.event_type.id == 1:
            event_act = occurrence.event.eventact
            workers = event_act.participants.all()
            self.convocation_sent = event_act.convocation_sent
            self.patient = event_act.patient
            self.patient_record_id = event_act.patient.id
            self.patient_record_paper_id = event_act.patient.paper_id
            self.workers_initial = ""
            self.workers_code = []
            self.workers = workers
            for worker in workers:
                if worker.first_name:
                    self.workers_initial += " " + worker.first_name.upper()[0]
                self.workers_initial += worker.last_name.upper()[0]
                self.workers_code.append("%s-%s" % (worker.id, worker.last_name.upper()))
            self.act_type = event_act.act_type.name
            self.act_state = event_act.get_state().state_name
            if self.act_state not in ('NON_VALIDE', 'VALIDE', 'ACT_DOUBLE'):
                self.act_absence = VALIDATION_STATES.get(self.act_state)
            state = event_act.get_state()
            display_name = VALIDATION_STATES[state.state_name]
            if not state.previous_state:
                state = None
            validation_states = None
            if service in services:
                validation_states = dict(VALIDATION_STATES)
                if not 'CMPP' in [s.name for s in services] and \
                        'ACT_DOUBLE' in validation_states:
                    validation_states.pop('ACT_DOUBLE')
            self.validation = (event_act, state, display_name, validation_states)
        else:
            self.event_type = occurrence.event.event_type

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

def get_daily_appointments(date, worker, service, time_tables, occurrences, holidays):
    """
    """
    appointments = []

    timetables_set = IntervalSet((t.to_interval(date) for t in time_tables))
    occurrences_set = IntervalSet((o.to_interval() for o in occurrences))
    holidays_set = IntervalSet((h.to_interval(date) for h in holidays))
    busy_occurrences_set = IntervalSet((o.to_interval() for o in occurrences if not o.is_event_absence()))
    for free_time in timetables_set - (busy_occurrences_set+holidays_set):
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
