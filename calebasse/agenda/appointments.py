# -*- coding: utf-8 -*-

from django.db.models import Q
from datetime import datetime, time

from calebasse.actes.models import EventAct
from calebasse.agenda.models import Occurrence
from calebasse.personnes.models import TimeTable

class Appointment(object):

    def __init__(self, title=None, begin_time=None, type=None,
            length=None, description=None, room=None, convocation_sent=None,
            service_name=None, patient_record_id=None, event_id=None):
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
            self.convocation_sent = event_act.convocation_sent
            self.patient_record_id = event_act.patient.id

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


def get_daily_appointments(date, worker, service):
    """
    """
    appointments = []
    weekday_mapping = {
            '0': u'dimanche',
            '1': u'lundi',
            '2': u'mardi',
            '3': u'mercredi',
            '4': u'jeudi',
            '5': u'vendredi',
            '6': u'samedi'
            }
    weekday = weekday_mapping[date.strftime("%w")]
    time_tables = TimeTable.objects.filter(worker=worker).\
            filter(service=service).\
            filter(weekday=weekday).\
            filter(start_date__lte=date).\
            filter(Q(end_date=None) |Q(end_date__gte=date)).\
            order_by('start_date')

    appointments = []
    occurrences = Occurrence.objects.daily_occurrences(date, [worker]).order_by('start_time')
    for occurrence in occurrences:
        appointment = Appointment()
        appointment.init_from_occurrence(occurrence, service)
        appointments.append(appointment)
        # Find free times between occurrences in time_tables
        next_occurrences = Occurrence.objects.filter(start_time__gte=occurrence.end_time).order_by('start_time')
        if next_occurrences:
            next_occurrence = next_occurrences[0]
            if not Occurrence.objects.filter(end_time__gt=occurrence.end_time).filter(end_time__lt=next_occurrence.start_time):
                for time_table in time_tables:
                    start_time_table =  datetime(date.year, date.month, date.day,
                            time_table.start_time.hour, time_table.start_time.minute)
                    end_time_table =  datetime(date.year, date.month, date.day,
                            time_table.end_time.hour, time_table.end_time.minute)
                    if (occurrence.end_time >= start_time_table) and (next_occurrence.start_time < end_time_table):
                        delta = next_occurrence.start_time - occurrence.end_time
                        if delta.seconds > 0:
                            delta_minutes = delta.seconds / 60
                            appointment = Appointment()
                            appointment.init_free_time(delta_minutes, time(occurrence.end_time.hour, occurrence.end_time.minute))
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
        start_datetime = datetime(date.year, date.month, date.day,
            time_table.start_time.hour, time_table.start_time.minute)
        end_datetime = datetime(date.year, date.month, date.day,
            time_table.end_time.hour, time_table.end_time.minute)
        smallest = Occurrence.objects.smallest_start_in_range(start_datetime, end_datetime, [worker])
        biggest = Occurrence.objects.biggest_end_in_range(start_datetime, end_datetime, [worker])
        if not smallest and not biggest:
            delta = end_datetime - start_datetime
            delta = delta.seconds / 60
            appointment = Appointment()
            appointment.init_free_time(delta,
                    time(start_datetime.hour, start_datetime.minute))
            appointments.append(appointment)
        if smallest:
            delta = smallest.start_time - start_datetime
            delta = delta.seconds / 60
            appointment = Appointment()
            appointment.init_free_time(delta,
                    time(start_datetime.hour, start_datetime.minute))
            appointments.append(appointment)
        if biggest:
            delta = end_datetime - biggest.end_time
            delta = delta.seconds / 60
            appointment = Appointment()
            appointment.init_free_time(delta,
                    time(biggest.end_time.hour, biggest.end_time.minute))
            appointments.append(appointment)

    appointments = sorted(appointments, key=lambda app: app.begin_time)
    return appointments

