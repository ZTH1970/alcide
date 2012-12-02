
from ajax_select import LookupChannel
from calebasse.dossiers.models import PatientRecord

class PatientRecordLookup(LookupChannel):

    model = PatientRecord
    search_field = 'display_name'

    def get_query(self,q,request):
        qs = super(PatientRecordLookup, self).get_query(q, request)
        if request.COOKIES.has_key('home-service'):
            service = request.COOKIES['home-service'].upper().replace('-', ' ')
            qs = qs.filter(service__name=service)
        return qs

