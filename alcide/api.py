import datetime

from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from alcide.actes.models import Act
from alcide.agenda.models import Event, EventWithAct
from alcide.dossiers.models import PatientRecord, PatientAddress


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        authorization = Authorization()

    def obj_get(self, bundle, **kwargs):
        '''If a date parameter is passed, use it to specialize the Event
           instance for this date.'''
        request = bundle.request
        date = None
        if 'date' in request.GET:
            date = request.GET['date']
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        obj = super(EventResource, self).obj_get(bundle, **kwargs)
        if date:
            obj = obj.today_occurrence(date)
        return obj

class EventWithActRessource(ModelResource):
    class Meta:
        queryset = EventWithAct.objects.all()
        resource_name = 'eventwithact'
        authorization = Authorization()

class PatientRecordRessource(ModelResource):
    class Meta:
        queryset = PatientRecord.objects.all()
        resource_name = 'patientrecord'
        authorization = Authorization()

class PatientAddressRessource(ModelResource):
    class Meta:
        queryset = PatientAddress.objects.all()
        resource_name = 'patientaddress'
        authorization = Authorization()

class ActRessource(ModelResource):
    class Meta:
        queryset = Act.objects.all()
        resource_name = 'act'
        authorization = Authorization()

patientaddress_ressource = PatientAddressRessource()
event_resource = EventResource()
eventwithact_resource = EventWithActRessource()
patientrecord_resource = PatientRecordRessource()
act_ressource = ActRessource()

