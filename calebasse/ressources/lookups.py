
from ajax_select import LookupChannel
from calebasse.personnes.models import Worker

class WorkerOrGroupLookup(LookupChannel):
    model = Worker
    search_field = 'display_name'
    # TODO: also look for groups
