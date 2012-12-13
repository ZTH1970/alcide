
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from calebasse.agenda.models import Event, Occurrence
from calebasse.dossiers.models import PatientRecord, PatientAddress


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        authorization = DjangoAuthorization()

class OccurrenceResource(ModelResource):
    class Meta:
        queryset = Occurrence.objects.all()
        resource_name = 'occurrence'
        authorization = DjangoAuthorization()

class PatientRecordRessource(ModelResource):
    class Meta:
        queryset = PatientRecord.objects.all()
        resource_name = 'patientrecord'
        authorization = DjangoAuthorization()

class PatientAddressRessource(ModelResource):
    class Meta:
        queryset = PatientAddress.objects.all()
        resource_name = 'patientaddress'
        authorization = DjangoAuthorization()

patientaddress_ressource = PatientAddressRessource()
event_resource = EventResource()
occurrence_resource = OccurrenceResource()
patientrecord_resource = PatientRecordRessource()

