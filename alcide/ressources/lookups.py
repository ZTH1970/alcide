# -*- coding: utf-8 -*-
import itertools
import re

from django.db.models import Q

from alcide.cbv import HOME_SERVICE_COOKIE
from alcide.lookups import AlcideLookup
from alcide.personnes.models import Worker
from alcide.ressources.models import Service, School

class FakeGroup:
    pk = None
    label = None

    def __init__(self, pk, label):
        self.pk = pk
        self.label = label

    def __unicode__(self):
        return u'Groupe: %s' % self.label


class WorkerOrGroupLookup(AlcideLookup):
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

class SchoolLookup(AlcideLookup):
    model = School
    search_field = 'name'
    query_words = []

    def get_query(self, q, request):
        service = ''
        if request.COOKIES.has_key(HOME_SERVICE_COOKIE):
            service = request.COOKIES[HOME_SERVICE_COOKIE]
        words = q.split()
        self.query_words = words
        lookups = [Q(display_name__icontains=word) for word in words]
        return School.objects.filter(*lookups).\
                filter(services__slug=service).\
                filter(school_type__services__slug=service)

    def get_result(self, obj):
        return self.format_item_display(obj)

    def format_match(self, obj):
        display = obj.display_name
        for word in self.query_words:
            pattern = re.compile(r"(%s)" % word, re.IGNORECASE)
            display = re.sub(pattern, r"<strong>\1</strong>", display)
        return display

    def format_item_display(self, obj):
        return obj.display_name

