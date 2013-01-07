# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta

from django.http import HttpResponseRedirect, Http404
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages

from calebasse import cbv, models as cb_models
from calebasse.ressources.models import Service

import forms
import models


FILTER_CRITERIA = (
        'username',
        'first_name',
        'last_name',
        'email',
        'userworker__worker__display_name',
)


class AccessView(cbv.ListView):
    model = User
    template_name = 'personnes/acces.html'

    def get_queryset(self):
        qs = super(AccessView, self).get_queryset()
        identifier = self.request.GET.get('identifier')
        if identifier:
            for part in identifier.split():
                filters = []
                for criteria in FILTER_CRITERIA:
                    q = Q(**{criteria+'__contains': part})
                    filters.append(q)
                qs = qs.filter(reduce(Q.__or__, filters))
        qs = qs.prefetch_related('userworker__worker')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(AccessView, self).get_context_data(**kwargs)
        ctx['active_list'] = ctx['object_list'].filter(is_active=True)
        ctx['inactive_list'] = ctx['object_list'].filter(is_active=False)
        return ctx


class AccessUpdateView(cbv.ServiceFormMixin, cbv.UpdateView):
    model = User
    template_name = 'personnes/acces-update.html'
    form_class = forms.UserForm
    success_url = '../'


class WorkerView(cbv.ListView):
    model = models.Worker
    template_name = 'personnes/workers.html'

    def get_form(self):
        return forms.WorkerSearchForm(data=self.request.GET or None)

    def get_queryset(self):
        qs = super(WorkerView, self).get_queryset()
        qs = qs.select_related()
        qs = qs.prefetch_related('services')
        form = self.get_form()
        if form.is_valid():
            cleaned_data = form.cleaned_data
            last_name = cleaned_data.get('last_name')
            first_name = cleaned_data.get('first_name')
            profession = cleaned_data.get('profession')
            intervene_status = cleaned_data.get('intervene_status')
            if last_name:
                qs = qs.filter(last_name__icontains=last_name)
            if first_name:
                qs = qs.filter(first_name__icontains=first_name)
            if profession:
                qs = qs.filter(type=profession)
            if intervene_status and 0 < len(intervene_status) < 2:
                qs = qs.filter(enabled=intervene_status[0] == 'a')
        else:
            # only display current workers by default
            qs = qs.filter(enabled=True)
        today = date.today()
        if models.Holiday.objects.for_service(self.service).future() \
                .filter(start_date__lte=today).exists():
            for worker in qs:
                worker.holiday = True
        else:
            qs2 = models.Holiday.objects.today()
            worker_dict = dict(((w.id, w) for w in qs))
            for worker in qs:
                worker.holiday = False
            for holiday in qs2:
                if holiday.worker.id in worker_dict:
                    worker_dict[holiday.worker.id].holiday = True
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(WorkerView, self).get_context_data(**kwargs)
        ctx['search_form'] = self.get_form()
        return ctx

homepage = cbv.TemplateView.as_view(template_name='personnes/index.html')


user_listing = AccessView.as_view()


class UserCreateView(cbv.ServiceFormMixin, cbv.CreateView):
    model=User
    success_url='../'
    form_class=forms.UserForm
    template_name='calebasse/simple-form.html'
    template_name_suffix='_new.html'


user_new = UserCreateView.as_view()
user_update = AccessUpdateView.as_view()
user_delete = cbv.DeleteView.as_view(model=User)


class WorkerUpdateView(cbv.MultiUpdateView):
    model = models.Worker
    forms_classes = {
            'id': forms.WorkerIdForm,
            'services': forms.WorkerServiceForm
    }
    template_name = 'personnes/worker_update.html'
    success_url = './'

    def get_context_data(self, **kwargs):
        ctx = super(WorkerUpdateView, self).get_context_data(**kwargs)
        _timetables = defaultdict(lambda: [])
        for timetable in self.object.timetable_set.order_by('start_time'):
            _timetables[timetable.weekday].append(timetable)
        timetable = []
        for weekday, name in models.TimeTable.WEEKDAYS:
            timetable.append({
                'weekday': name,
                'schedules': _timetables[weekday]})
        ctx['weekdays'] = list(models.TimeTable.WEEKDAYS)
        ctx['timetables'] = timetable
        ctx['holidays'] = models.Holiday.objects \
                            .for_worker(self.object) \
                            .future() \
                            .order_by('start_date')
        try:
            holiday = models.Holiday.objects \
                    .for_worker(self.object) \
                    .today()[0]
        except IndexError:
            holiday = None
        ctx['holiday'] = holiday
        return ctx

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, u'Modification enregistrée avec succès.')
        return super(WorkerUpdateView, self).form_valid(form)


class WorkerScheduleUpdateView(cbv.UpdateView):
    model = models.Worker
    form_class = forms.TimetableFormSet
    success_url = '../'
    template_name = 'personnes/worker_schedule_update.html'

    def get_form_kwargs(self):
        kwargs = super(WorkerScheduleUpdateView, self).get_form_kwargs()
        kwargs['queryset'] = models.TimeTable.objects.filter(weekday=self.weekday).prefetch_related('services')
        kwargs['initial'] = [{ 'services': Service.objects.all().values_list('pk', flat=True) }] * 3
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(WorkerScheduleUpdateView, self).get_context_data(**kwargs)
        ctx['weekday'] = models.TimeTable.WEEKDAYS[self.weekday][1]
        return ctx

    def dispatch(self, *args, **kwargs):
        self.weekday = int(kwargs['weekday'])
        if self.weekday > 6:
            raise Http404()
        return super(WorkerScheduleUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        instances = form.save(commit=False)
        for instance in instances:
            instance.weekday = self.weekday
            instance.save()
        form.save_m2m()
        return HttpResponseRedirect('')


class WorkerHolidaysUpdateView(cbv.UpdateView):
    model = models.Worker
    form_class = forms.HolidayFormSet
    success_url = '../'
    template_name = 'personnes/worker_holidays_update.html'

    def get_success_url(self):
        return self.success_url


worker_listing = WorkerView.as_view()
worker_new = cbv.CreateView.as_view(model=models.Worker,
        template_name='calebasse/simple-form.html',
        success_url='../')
worker_update = WorkerUpdateView.as_view()
worker_schedule_update = WorkerScheduleUpdateView.as_view()
worker_holidays_update = WorkerHolidaysUpdateView.as_view()
worker_delete = cbv.DeleteView.as_view(model=models.Worker,
        template_name='calebasse/simple-form.html',
        success_url='../')


class HolidayView(cbv.TemplateView):
    months = 3
    template_name='personnes/holidays.html'

    def get_form(self):
        return forms.HolidaySearchForm(data=self.request.GET)

    def get_context_data(self, **kwargs):
        ctx = super(HolidayView, self).get_context_data(**kwargs)
        end_date = date.today() + relativedelta(months=self.months)
        qs = models.Holiday.objects.future().select_related('worker')
        today = date.today()
        future_qs = qs.for_period(today, end_date).select_related('worker')
        group_qs = models.Holiday.objects.for_service(self.service).select_related()
        current_qs = qs.today()
        form = self.get_form()
        if form.is_valid() and form.cleaned_data.get('start_date'):
            cleaned_data = form.cleaned_data
            start_date = cleaned_data['start_date']
            end_date = cleaned_data['end_date']
            future_qs = models.Holiday.objects \
                    .for_period(start_date, end_date) \
                    .for_service_workers(self.service)
            group_qs = group_qs.for_period(start_date, end_date)
            current_qs = []
        ctx['end_date'] = end_date
        ctx['current_holidays'] = current_qs
        future_holidays = defaultdict(lambda:[])
        for holiday in future_qs:
            key = (holiday.start_date.year, holiday.start_date.month, holiday.start_date.strftime('%B'))
            future_holidays[key].append(holiday)
        ctx['future_holidays'] = [ {
            'date': date(day=1, month=key[1], year=key[0]),
            'holidays': future_holidays[key]
          } for key in sorted(future_holidays.keys()) ]
        ctx['group_holidays'] = group_qs.order_by('-start_date')
        ctx['search_form'] = form
        return ctx


holiday_listing = HolidayView.as_view()


class GroupHolidayUpdateView(cbv.FormView):
    form_class = forms.GroupHolidayFormSet
    template_name = 'personnes/group_holiday_update.html'
    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super(GroupHolidayUpdateView, self).get_form_kwargs()
        qs = models.Holiday.objects.for_service(self.service)
        kwargs['queryset'] = qs
        kwargs['service'] = self.service
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(GroupHolidayUpdateView, self).form_valid(form)


group_holiday_update = GroupHolidayUpdateView.as_view()
