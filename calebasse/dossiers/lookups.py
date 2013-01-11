
from ajax_select import LookupChannel
from calebasse.dossiers.models import PatientRecord, PatientAddress
from django.core.exceptions import PermissionDenied

class PatientRecordLookup(LookupChannel):
    model = PatientRecord
    search_field = 'display_name'

    def get_query(self,q,request):
        qs = super(PatientRecordLookup, self).get_query(q, request)
        if request.COOKIES.has_key('home-service'):
            service = request.COOKIES['home-service'].upper().replace('-', ' ')
            qs = qs.filter(service__name=service)
        return qs

    def get_result(self,obj):
        if obj.paper_id:
            return obj.display_name + u' (' + obj.paper_id + u')'
        else:
            return obj.display_name

    def check_auth(self, request):
        if not request.user.is_authenticated():
            raise PermissionDenied

class PatientAddressLookup(LookupChannel):
    model = PatientAddress
    search_field = 'display_name'

    def get_query(self, q, request):
        qs = super(PatientAddressLookup, self).get_query(q, request)
        if request.session.has_key('patientrecord_id'):
            qs = qs.filter(patientcontact__id=request.session['patientrecord_id'])
        return qs

    def check_auth(self, request):
        if not request.user.is_authenticated():
            raise PermissionDenied
