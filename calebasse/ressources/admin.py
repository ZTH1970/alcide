from django.contrib import admin

from calebasse.ressources.models import ActType, TransportCompany, WorkerType, Service, Office, School, Room

admin.site.register(ActType)
admin.site.register(TransportCompany)
admin.site.register(WorkerType)
admin.site.register(Service)
admin.site.register(Office)
admin.site.register(Room)
admin.site.register(School)
