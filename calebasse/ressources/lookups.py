import itertools

from calebasse.lookups import CalebasseLookup
from calebasse.personnes.models import Worker
from calebasse.ressources.models import Service

class FakeGroup:
    pk = None
    label = None

    def __init__(self, pk, label):
        self.pk = pk
        self.label = label

    def __unicode__(self):
        return u'Groupe: %s' % self.label


class WorkerOrGroupLookup(CalebasseLookup):
    model = Worker
    search_field = 'last_name'
    enabled = True

    def get_query(self, q, request):
        service = None
        if q.startswith('group:'):
            service = Service.objects.get(pk=int(q[6:]))
        else:
            try:
                service = Service.objects.get(name__iexact=q)
            except Service.DoesNotExist:
                pass

        if service:
            kwargs = { "%s__istartswith" % self.search_field : q }
            group = FakeGroup('group:%s' % service.id, service.name)
            return itertools.chain([group], self.model.objects.for_service(service.id).order_by('last_name'))

        kwargs = { "%s__istartswith" % self.search_field : q }
        if self.enabled:
            return self.model.objects.filter(enabled=True).filter(**kwargs).order_by('last_name')
        return self.model.objects.filter(**kwargs).order_by('last_name')

    def get_result(self, obj):
        return self.format_item_display(obj)

    def format_match(self, obj):
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        if isinstance(obj, FakeGroup):
            text = obj.label
        else:
            text = obj.last_name.upper() + ' ' + obj.first_name
        return unicode(text)

class AllWorkerOrGroupLookup(WorkerOrGroupLookup):
    enabled = False
