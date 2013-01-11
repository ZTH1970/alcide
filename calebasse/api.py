
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from calebasse.actes.models import Act
from calebasse.agenda.models import Event
from calebasse.dossiers.models import PatientRecord, PatientAddress


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
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

class ActRessource(ModelResource):
    class Meta:
        queryset = Act.objects.all()
        resource_name = 'act'
        authorization = DjangoAuthorization()

patientaddress_ressource = PatientAddressRessource()
event_resource = EventResource()
patientrecord_resource = PatientRecordRessource()
act_ressource = ActRessource()

