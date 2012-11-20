from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta

from django.http import HttpResponseRedirect, Http404
from django.db.models import Q
from django.contrib.auth.models import User

from calebasse import cbv, models as cb_models

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
                qs = qs.filter(type__intervene=intervene_status[0] == 'a')
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
user_new = cbv.CreateView.as_view(model=User,
        success_url='../',
        form_class=forms.UserForm,
        template_name='calebasse/simple-form.html',
        template_name_suffix='_new.html')
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
        for weekday in cb_models.WeekdayField.WEEKDAYS:
            timetable.append({
                'weekday': weekday,
                'schedules': _timetables[weekday]})
        ctx['weekdays'] = cb_models.WeekdayField.WEEKDAYS
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

class WorkerScheduleUpdateView(cbv.UpdateView):
    model = models.Worker
    form_class = forms.TimetableFormSet
    success_url = '../'
    template_name = 'personnes/worker_schedule_update.html'

    def get_form_kwargs(self):
        kwargs = super(WorkerScheduleUpdateView, self).get_form_kwargs()
        kwargs['weekday'] = self.kwargs['weekday']
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(WorkerScheduleUpdateView, self).get_context_data(**kwargs)
        ctx['weekday'] = self.kwargs['weekday']
        return ctx

    def dispatch(self, *args, **kwargs):
        if kwargs['weekday'] not in cb_models.WeekdayField.WEEKDAYS:
            raise Http404()
        return super(WorkerScheduleUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        instances = form.save(commit=False)
        for instance in instances:
            instance.weekday = self.kwargs['weekday']
            instance.service = self.service
            instance.save()
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
        qs = models.Holiday.objects.for_service_workers(self.service).future()
        today = date.today()
        future_qs = qs.for_period(today, end_date)
        annual_qs = models.Holiday.objects.for_service(self.service)
        current_qs = qs.today()
        form = self.get_form()
        if form.is_valid() and form.cleaned_data.get('start_date'):
            cleaned_data = form.cleaned_data
            start_date = cleaned_data['start_date']
            end_date = cleaned_data['end_date']
            future_qs = models.Holiday.objects \
                    .for_period(start_date, end_date) \
                    .for_service_workers(self.service)
            annual_qs = annual_qs.for_period(start_date, end_date)
            current_qs = []
        ctx['current_holidays'] = current_qs
        future_holidays = defaultdict(lambda:[])
        for holiday in future_qs:
            key = (holiday.start_date.year, holiday.start_date.month, holiday.start_date.strftime('%B'))
            future_holidays[key].append(holiday)
        ctx['future_holidays'] = [ { 
            'date': date(day=1, month=key[1], year=key[0]),
            'holidays': future_holidays[key] 
          } for key in sorted(future_holidays.keys()) ]
        ctx['annual_holidays'] = annual_qs
        ctx['search_form'] = form
        return ctx


holiday_listing = HolidayView.as_view()


class YearlyHolidayUpdateView(cbv.FormView):
    form_class = forms.YearlyHolidayFormSet
    template_name = 'personnes/yearly_holiday_update.html'

    def get_success_url(self):
        return '../'

    def get_form_kwargs(self):
        kwargs = super(YearlyHolidayUpdateView, self).get_form_kwargs()
        qs = models.Holiday.objects.for_service(self.service)
        kwargs['queryset'] = qs
        kwargs['service'] = self.service
        return kwargs


yearly_holiday_update = YearlyHolidayUpdateView.as_view()
