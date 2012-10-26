# -*- coding: utf-8 -*-

from django.db.models import Q
from datetime import datetime, time

from interval import IntervalSet

from calebasse.actes.models import EventAct
from calebasse.agenda.models import Occurrence
from calebasse.personnes.models import TimeTable

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
        self.service_name = None
        self.patient_record_id = None
        self.event_id = None
        self.service = None
        self.workers_initial = None
        self.act_type = None
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
        self.length = delta.seconds / 60
        self.title = occurrence.title
        services = occurrence.event.services.all()
        if services:
            self.service = services[0].name.lower()
        self.__set_time(time(occurrence.start_time.hour, occurrence.start_time.minute))
        if service in occurrence.event.services.all():
            self.type = "busy-here"
        else:
            self.type = "busy-elsewhere"
            self.service_name = service.name
        self.event_id = occurrence.event.id
        if occurrence.event.room:
            self.room = occurrence.event.room.name
        self.description = occurrence.event.description
        if occurrence.event.event_type.label == 'patient_appointment':
            event_act = occurrence.event.eventact
            workers = event_act.participants.all()
            self.convocation_sent = event_act.convocation_sent
            self.patient_record_id = event_act.patient.id
            self.workers_initial = ""
            for worker in workers:
                self.workers_initial += " " + worker.first_name.upper()[0]
                self.workers_initial += worker.last_name.upper()[0]
            self.act_type = event_act.act_type.name

    def init_free_time(self, length, begin_time):
        """ """
        self.type = "free"
        self.length = length
        self.__set_time(begin_time)


    def init_start_stop(self, title, time):
        """
        title: Arrivee ou Depart
        """
        self.type = "info"
        self.title = title
        self.__set_time(time)

def get_daily_appointments(date, worker, service, time_tables, occurrences):
    """
    """
    appointments = []

    timetables_set = IntervalSet((t.to_interval(date) for t in time_tables))
    occurrences_set = IntervalSet((o.to_interval() for o in occurrences))
    for free_time in timetables_set - occurrences_set:
        if free_time:
            delta = free_time.upper_bound - free_time.lower_bound
            delta_minutes = delta.seconds / 60
            appointment = Appointment()
            appointment.init_free_time(delta_minutes,
                    time(free_time.lower_bound.hour, free_time.upper_bound.minute))
            appointments.append(appointment)
    for occurrence in occurrences:
        appointment = Appointment()
        appointment.init_from_occurrence(occurrence, service)
        appointments.append(appointment)
    for time_table in time_tables:
        appointment = Appointment()
        appointment.init_start_stop(u"Arrivée",
            time(time_table.start_time.hour, time_table.start_time.minute))
        appointments.append(appointment)
        appointment = Appointment()
        appointment.init_start_stop(u"Départ",
            time(time_table.end_time.hour, time_table.end_time.minute))
        appointments.append(appointment)

    appointments = sorted(appointments, key=lambda app: app.begin_time)
    return appointments

