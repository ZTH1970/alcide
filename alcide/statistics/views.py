# -*- coding: utf-8 -*-
import urllib

from datetime import datetime

from django.core.files import File
from django.http import HttpResponse

from alcide.cbv import TemplateView, FormView
from alcide.statistics import forms

from statistics import STATISTICS, Statistic


class StatisticsHomepageView(TemplateView):
    template_name = 'statistics/index.html'

    def get_context_data(self, **kwargs):
        context = super(StatisticsHomepageView, self).get_context_data(**kwargs)
        statistics = dict()
        for name, statistic in STATISTICS.iteritems():
            if not statistic.get('services') or \
                    self.service.name in statistic.get('services'):
                statistics.setdefault(statistic['category'], []).append((name,
                    statistic))
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
        inputs['inscriptions'] = self.request.GET.get('inscriptions')
        inputs['no_synthesis'] = self.request.GET.get('no_synthesis')
        statistic = Statistic(name, inputs)
        context['dn'] = statistic.display_name
        context['data_tables_set'] = statistic.get_data()
        return context


class StatisticsFormView(FormView):
    template_name = 'statistics/form.html'

    def dispatch(self, request, **kwargs):
        self.name = kwargs.get('name')
        return super(StatisticsFormView, self).dispatch(request, **kwargs)

    def get_form_class(self):
        if self.name == 'annual_activity':
            return forms.AnnualActivityForm
        elif self.name == 'patients_synthesis':
            return forms.PatientsSynthesisForm
        elif self.name == 'patients_details':
            return forms.PatientsTwoDatesForm
        elif self.name in ('active_patients_by_state_only',
                'patients_protection', 'patients_contact'):
            return forms.OneDateForm
        elif self.name == 'patients_per_worker_for_period':
            return forms.PatientsPerWorkerForPeriodForm
        elif self.name in ('active_patients_with_act', 'closed_files',
                'patients_synthesis', 'acts_synthesis',
                'acts_synthesis_cmpp', 'mises', 'deficiencies'):
            return forms.TwoDatesForm
        else:
            return forms.ParticipantsPatientsTwoDatesForm

    def form_valid(self, form):
        if 'display_or_export' in form.data:
            inputs = dict()
            inputs['service'] = self.service
            inputs['start_date'] = form.data.get('start_date')
            inputs['end_date'] = form.data.get('end_date')
            inputs['participants'] = form.data.get('participants')
            inputs['patients'] = form.data.get('patients')
            inputs['inscriptions'] = form.data.get('inscriptions')
            inputs['no_synthesis'] = 'no_synthesis' in form.data
            statistic = Statistic(self.name, inputs)
            path = statistic.get_file()
            content = File(file(path))
            response = HttpResponse(content, 'text/csv')
            response['Content-Length'] = content.size
            dest_filename = "%s--%s.csv" \
                % (datetime.now().strftime('%Y-%m-%d--%H:%M:%S'),
                statistic.display_name)
            response['Content-Disposition'] = \
                'attachment; filename="%s"' % dest_filename
            return response
        return super(StatisticsFormView, self).form_valid(form)

    def get_success_url(self):
        qs = urllib.urlencode(self.request.POST)
        target = '../../detail/%s?%s' % (self.kwargs.get('name'), qs)
        return target
