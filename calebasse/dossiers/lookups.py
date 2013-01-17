# -*- coding: utf-8 -*-

from ajax_select import LookupChannel
from calebasse.dossiers.models import PatientRecord, PatientAddress
from django.core.exceptions import PermissionDenied

from django.db.models import Q

class PatientRecordLookup(LookupChannel):
    model = PatientRecord
    search_field = 'display_name'
    homonym = False

    def get_query(self,q,request):
        qs = self.model.objects.filter( Q(first_name__istartswith=q) | \
                Q(last_name__istartswith=q)).order_by(self.search_field)
        if request.COOKIES.has_key('home-service'):
            service = request.COOKIES['home-service'].upper().replace('-', ' ')
            qs = qs.filter(service__name=service)
        #nb = qs.count()
        #nb_distinct = qs.distinct('display_name').count()
        #if nb != nb_distinct:
        #    self.homonym = True
        qs.prefetch_related('last_state__status')
        return qs

    def format_match(self,obj):
        texte = obj.display_name
        if obj.paper_id:
            texte += u' (N° : ' + obj.paper_id + u')'
        if obj.last_state:
            texte += u' (Statut : %s)' % obj.last_state.status.name
        return self.format_item_display(texte)

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
