from django.contrib import admin

from calebasse.actes.models import Act, EventAct
from calebasse.agenda.models import Event
from calebasse.personnes.models import Worker, TimeTable
from calebasse.ressources.models import TransportCompany, WorkerType, Service, Office, School, Room

admin.site.register(Act)
admin.site.register(EventAct)
admin.site.register(Event)
admin.site.register(Worker)
admin.site.register(TimeTable)
admin.site.register(TransportCompany)
admin.site.register(WorkerType)
admin.site.register(Service)
admin.site.register(Office)
admin.site.register(Room)
admin.site.register(School)
