
from calebasse.lookups import CalebasseLookup

from models import Worker

class WorkerLookup(CalebasseLookup):
    model = Worker
    search_field = 'display_name'

    def get_query(self,q,request):
        kwargs = { "%s__icontains" % self.search_field : q }
        return self.model.objects.filter(enabled=True).filter(**kwargs).order_by(self.search_field)

    def get_result(self, obj):
        return self.format_item_display(obj)

    def format_match(self, obj):
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        text = obj.last_name.upper() + ' ' + obj.first_name
        return unicode(text)

class IntervenantLookup(WorkerLookup):
    model = Worker
    search_field = 'display_name'

    def get_query(self,q,request):
        qs = super(IntervenantLookup, self).get_query(q,request)
        return qs.filter(type__intervene=True)
