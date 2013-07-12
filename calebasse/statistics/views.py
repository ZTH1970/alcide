# -*- coding: utf-8 -*-
import urllib

from calebasse.cbv import TemplateView, FormView
from calebasse.statistics import forms

from statistics import STATISTICS, Statistic


class StatisticsHomepageView(TemplateView):
    template_name = 'statistics/index.html'

    def get_context_data(self, **kwargs):
        context = super(StatisticsHomepageView, self).get_context_data(**kwargs)
        statistics = dict()
        for name, statistic in STATISTICS.iteritems():
            statistics.setdefault(statistic['category'], []).append((name,
                statistic['display_name']))
        context['statistics'] = statistics
        return context


class StatisticsDetailView(TemplateView):
    template_name = 'statistics/detail.html'

    def get_context_data(self, **kwargs):
        context = super(StatisticsDetailView, self).get_context_data(**kwargs)
        name = kwargs.get('name')
        inputs = dict()
        inputs['service'] = self.service
        inputs['start_date'] = self.request.GET.get('start_date')
        inputs['end_date'] = self.request.GET.get('end_date')
        inputs['participants'] = self.request.GET.get('participants')
        inputs['patients'] = self.request.GET.get('patients')
        statistic = Statistic(name, inputs)
        target = 'detail/%s?%s' % (self.kwargs.get('name'),
            self.request.META['QUERY_STRING'])
        context['url'] = target
        context['dn'] = statistic.display_name
        context['data'] = statistic.get_data()
        return context


class StatisticsFormView(FormView):
    form_class = forms.StatForm
    template_name = 'statistics/form.html'
    success_url = '..'

    def get_success_url(self):
        qs = urllib.urlencode(self.request.POST)
        target = '../../detail/%s?%s' % (self.kwargs.get('name'), qs)
        return target
