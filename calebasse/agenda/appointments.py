
from calebasse.agenda.models import Occurence
from calebasse.personnes.models import TimeTable

class Appointment(object):

    def __init__(self, title=None, begin_hour=None, type=None,
            length=None, description=None, room=None, convocation_sent=None,
            service_name=None):
        """ """
        self.title = title
        self.begin_hour = begin_hour
        self.type = type
        self.length = length
        self.description = description
        self.room = room
        self.convocation_sent = None
        self.service_name = None

    def load_from_occurence(self, occurence, service):
        """ """
        delta = occurence.end_time - occurence.start_time
        self.length = (delta.hours * 60) + dela.minutes
        self.title = occurence.title
        self.begin_hour = occurence.start_time.hours
        if service in occurence.services:
            self.type = "busy-here"
        else:
            self.type = "busy-elsewhere"
            self.service_name = service.name
        self.room = occurence.room.name
        self.convocation_sent = occurence.convocation_sent
        self.description = occurence.description

def get_daily_appointments(date, worker, service):
    """
    """
    weekday_mapping = {
            '0': 'dimanche',
            '1': 'lundi',
            '2': 'mardi',
            '3': 'mercredi',
            '4': 'jeudi',
            '5': 'vendredi'
            '6': 'samedi'
            }
    weekday = weekday_mapping[date.strftime("%w")]
    time_tables = TimeTable.objects.filter(worker=worker).\
            filter(service=service).\
            filter(weekday=weekday).\
            filter(start_date__lte=date).\
            filter(end_date__gte=date)
    occurences = Occurence.objects.daily_occurrences(date, [worker])


