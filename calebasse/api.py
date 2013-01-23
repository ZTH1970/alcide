import datetime

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

    def obj_get(self, request, **kwargs):
        '''If a date parameter is passed, use it to specialize the Event
           instance for this date.'''
        date = None
        if 'date' in request.GET:
            date = request.GET['date']
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        obj = super(EventResource, self).obj_get(request, **kwargs)
        if date:
            obj = obj.today_occurrence(date)
        return obj

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

