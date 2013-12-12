# -*- coding: utf-8 -*-

from calebasse.lookups import CalebasseLookup
from calebasse.dossiers.models import PatientRecord, PatientAddress
from itertools import chain

class PatientRecordLookup(CalebasseLookup):
    model = PatientRecord
    search_field = 'last_name'
    homonym = False

    def get_query(self,q,request):
        kwargs = { "%s__istartswith" % self.search_field : q }
        not_closed_filter_field = 'last_state__status__name'

        qs = self.model.objects.filter(**kwargs).order_by(self.search_field)

        if request.COOKIES.has_key('home-service'):
            service = request.COOKIES['home-service'].upper().replace('-', ' ')
            qs = qs.filter(service__name=service)
        #nb = qs.count()
        #nb_distinct = qs.distinct('display_name').count()
        #if nb != nb_distinct:
        #    self.homonym = True
        qs.prefetch_related('last_state__status')
        qs.query.order_by = [not_closed_filter_field, ]

        # filtering all closed records to put them at the end
        separation_criteria = {'last_state__status__name': 'Clos'}
        closed = qs.filter(**separation_criteria)
        qs = qs.exclude(**separation_criteria)

        qs = qs.order_by('-%s' % not_closed_filter_field)

        return chain(qs, closed)

    def format_match(self,obj):
        return self.format_item_display(texte)

    def get_result(self, obj):
        return self.format_item_display(obj)

    def format_match(self, obj):
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        text = obj.last_name.upper() + ' ' + obj.first_name
        if obj.paper_id or obj.last_state:
            text += u' ('
        if obj.paper_id:
            text += obj.paper_id
            if obj.last_state:
                text += u' - '
        if obj.last_state:
            text += obj.last_state.status.name
        if obj.paper_id or obj.last_state:
            text += u')'
        return unicode(text)

class PatientAddressLookup(CalebasseLookup):
    model = PatientAddress
    search_field = 'display_name'

    def get_query(self, q, request):
        qs = super(PatientAddressLookup, self).get_query(q, request)
        if request.session.has_key('patientrecord_id'):
            qs = qs.filter(patientcontact__id=request.session['patientrecord_id'])
        return qs

