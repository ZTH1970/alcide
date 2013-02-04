
from ajax_select import LookupChannel
from models import Worker

class Worker(LookupChannel):
    model = Worker
    search_field = 'display_name'

    def get_query(self,q,request):
        kwargs = { "%s__icontains" % self.search_field : q }

    def get_result(self, obj):
        return self.format_item_display(obj)

    def format_match(self, obj):
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        text = obj.last_name.upper() + ' ' + obj.first_name
        return unicode(text)

