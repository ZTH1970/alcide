from django.db.models import Q
from django.contrib.auth.models import User

from calebasse import cbv

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
                    print 'q', q
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


worker_listing = WorkerView.as_view()
worker_new = cbv.CreateView.as_view(model=models.Worker,
        template_name='calebasse/simple-form.html',
        success_url='../')
worker_update = cbv.UpdateView.as_view(model=models.Worker,
        template_name='calebasse/simple-form.html',
        success_url='./')
worker_delete = cbv.DeleteView.as_view(model=models.Worker,
        template_name='calebasse/simple-form.html',
        success_url='../')
