# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import date
from interval import IntervalSet

from dateutil.relativedelta import relativedelta

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.dateformat import format as date_format
from django.views.decorators.csrf import csrf_exempt

from calebasse import cbv, models as cb_models
from calebasse.ressources.models import Service

import json

from calebasse.decorators import super_user_only

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


user_listing = super_user_only(AccessView.as_view())


class UserCreateView(cbv.ServiceFormMixin, cbv.CreateView):
    model=User
    success_url='../'
    form_class=forms.UserForm
    template_name='calebasse/simple-form.html'
    template_name_suffix='_new.html'

class UserDeleteView(cbv.DeleteView):
    model = User
    success_url = "../../"
    template_name = 'calebasse/generic_confirm_delete.html'


user_new = super_user_only(UserCreateView.as_view())
user_update = super_user_only(AccessUpdateView.as_view())
user_delete = super_user_only(UserDeleteView.as_view())


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
        success_url='../../')


class HolidayView(cbv.TemplateView):
    months = 3
    template_name='personnes/holidays.html'

    def get_form(self):
        return forms.HolidaySearchForm(data=self.request.GET)

    def get_context_data(self, **kwargs):
        ctx = super(HolidayView, self).get_context_data(**kwargs)
        form = forms.HolidaySearchForm(data=self.request.GET)

        today = date.today()
        filter_start_date = today
        filter_end_date = date.today() + relativedelta(months=self.months)

        if form.is_valid():
            if form.cleaned_data.get('start_date'):
                filter_start_date = form.cleaned_data.get('start_date')
            if form.cleaned_data.get('end_date'):
                filter_end_date = form.cleaned_data.get('end_date')

        workers = models.Worker.objects.filter(enabled=True)
        holidays = models.Holiday.objects \
                .filter(end_date__gte=filter_start_date,
                        start_date__lte=filter_end_date) \
                .select_related('worker', 'service')
        holiday_by_worker = defaultdict(lambda: [])
        all_holidays = holidays.filter(worker__isnull=True)

        for worker in workers:
            holiday_by_worker[worker] = list(all_holidays)

        for holiday in holidays.filter(worker__isnull=False):
            holiday_by_worker[holiday.worker].append(holiday)

        def holiday_url(holiday):
            if holiday.worker:
                return reverse('worker_update', kwargs=dict(
                    service=self.service.slug, pk=holiday.worker.pk))
            else:
                slug = holiday.service.slug if holiday.service else self.service.slug
                return reverse('group-holiday-update', kwargs=dict(
                    service=slug))

        currents = []
        futures = defaultdict(lambda: [])
        for worker, holidays in holiday_by_worker.iteritems():
            for holiday in holidays:
                url = holiday_url(holiday)
                holiday_tpl = dict(worker=worker.display_name, holiday=holiday, url=url)
                if holiday.start_date <= today <= holiday.end_date:
                    currents.append(holiday_tpl)
                start_date = max(holiday.start_date, filter_start_date)
                month_name = date_format(start_date, 'F')
                key = start_date.year, start_date.month, month_name
                futures[key].append(holiday_tpl)

        future_holidays = []
        for key in sorted(futures.keys()):
            future_holidays.append(dict(
                month=key[2],
                holidays=futures[key]))
        future_holidays2 = []
        for i in range(0, len(future_holidays), 2):
            future_holidays2.append(future_holidays[i:i+2])

        ctx['end_date'] = filter_end_date
        ctx['current_holidays'] = currents
        ctx['future_holidays'] = future_holidays2
        ctx['group_holidays'] = all_holidays.order_by('-start_date')
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

class HolidayManagement(object):

    def render_to_json(self, id, context, err = 0, **kwargs):
        data = {'err': err, 'id': id, 'content': context}
        response = json.dumps(data)
        kwargs['content_type'] = 'application/json'
        return HttpResponse(response, **kwargs)

    def update_post_data(self, request):
        worker = models.Worker.objects.get(pk = self.kwargs['worker_pk'])
        post = request.POST.copy()
        post.update({'worker': worker.id})
        return worker, post

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax:
            instance = form.instance
            status = ''
            if instance.is_current() and instance.service:
                status = u'congés annuels, en cours'
            elif instance.is_current():
                status = u'en cours'
            elif instance.service:
                status = u'congés annuels'

            context = (('period', '%s' % instance),
                       ('status', status),
                       ('type', '%s' % instance.holiday_type),
                       ('comment', instance.comment)
                       )
            return self.render_to_json(instance.id, context)
        return super(HolidayManagement, self).form_valid(form)

class HolidayCreateView(HolidayManagement, cbv.CreateView):
    model = models.Holiday
    form_class = forms.HolidayForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(HolidayCreateView, self).get_form_kwargs(*args, **kwargs)
        return kwargs

    def post(self, request, *args, **kwargs):
        worker, post = self.update_post_data(request)
        form = self.form_class(post)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return super(HolidayCreateView, self).post(request, *args, **kwargs)

create_holiday = HolidayCreateView.as_view()

class EditHolidayView(HolidayManagement, cbv.FormView):
    template_name = 'personnes/holiday_update_form.html'
    form_class = forms.HolidayForm
    model = models.Holiday

    def get_form_kwargs(self):
        kwargs = super(EditHolidayView, self).get_form_kwargs()
        kwargs['instance'] = self.model.objects.get(pk = self.kwargs['pk'])
        return kwargs

    def post(self, request, *args, **kwargs):
        worker, post = self.update_post_data(request)
        obj = self.model.objects.for_worker(worker).get(pk = kwargs['pk'])
        form = self.form_class(post, instance = obj)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


edit_holiday = EditHolidayView.as_view()

class DeleteHolidayView(cbv.DeleteView):
    model = models.Holiday
    template_name = 'personnes/holiday_update_form.html'

    def post(self, request, *args, **kwargs):
        response = HttpResponse('', content_type = 'application/json')
        context = {'err': 0, }
        try:
            worker = models.Worker.objects.get(pk = self.kwargs['worker_pk'])
            self.model.objects.for_worker(worker).get(pk = self.kwargs['pk']).delete()
        except Exception, e:
            context['error': e.message]
        response.content = json.dumps(context)
        return response

delete_holiday = DeleteHolidayView.as_view()

#user_delete = UserCreateView.as_view()

