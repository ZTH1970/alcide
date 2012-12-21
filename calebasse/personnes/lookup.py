
from ajax_select import LookupChannel
from models import Worker

class Worker(LookupChannel):
    model = Worker
    search_field = 'display_name'

    def get_query(self,q,request):
        kwargs = { "%s__icontains" % self.search_field : q }
        return self.model.objects.filter(enabled=True).filter(**kwargs).order_by(self.search_field)
