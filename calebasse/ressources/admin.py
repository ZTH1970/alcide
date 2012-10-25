from django.contrib import admin

from models import (ActType, CFTMEACode, FamilySituationType, HealthFund,
        InscriptionMotive, Job, Nationality, Office, ParentalAuthorityType,
        ParentalCustodyType, Room, School, SchoolTeacherRole,
        Service, SessionType, TransportCompany, TransportType,
        UninvoicableCode, WorkerType)

admin.site.register(ActType)
admin.site.register(CFTMEACode)
admin.site.register(FamilySituationType)
admin.site.register(HealthFund)
admin.site.register(InscriptionMotive)
admin.site.register(Job)
admin.site.register(Nationality)
admin.site.register(Office)
admin.site.register(ParentalAuthorityType)
admin.site.register(ParentalCustodyType)
admin.site.register(Room)
admin.site.register(School)
admin.site.register(SchoolTeacherRole)
admin.site.register(Service)
admin.site.register(SessionType)
admin.site.register(TransportCompany)
admin.site.register(TransportType)
admin.site.register(UninvoicableCode)
admin.site.register(WorkerType)
