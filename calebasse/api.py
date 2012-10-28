
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from calebasse.agenda.models import Event, Occurrence


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
