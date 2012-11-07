from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.views.generic import list as list_cbv, edit, base # ListView
# from django.views.generic.edit import # CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import resolve

from calebasse.ressources.models import Service

class ServiceViewMixin(object):
    service = None
    date = None
    popup = False

    def dispatch(self, request, **kwargs):
        self.popup = request.GET.get('popup')
        if 'service' in kwargs:
            self.service = get_object_or_404(Service, slug=kwargs['service'])
        if 'date' in kwargs:
            try:
                self.date = datetime.strptime(kwargs.get('date'),
                        '%Y-%m-%d').date()
            except (TypeError, ValueError):
                raise Http404
        return super(ServiceViewMixin, self).dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ServiceViewMixin, self).get_context_data(**kwargs)
        context['url_name'] = resolve(self.request.path).url_name
        context['popup'] = self.popup
        if self.service is not None:
            context['service'] = self.service.slug
            context['service_name'] = self.service.name

        if self.date is not None:
            context['date'] = self.date
            context['previous_day'] = self.date + relativedelta(days=-1)
            context['next_day'] = self.date + relativedelta(days=1)
            context['previous_month'] = self.date + relativedelta(months=-1)
            context['next_month'] = self.date + relativedelta(months=1)
        return context

class TemplateView(ServiceViewMixin, base.TemplateView):
    pass

class ModelNameMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(ModelNameMixin, self).get_context_data(**kwargs)
        ctx['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        ctx['model_verbose_name'] = self.model._meta.verbose_name
        return ctx

class ListView(ModelNameMixin, ServiceViewMixin, list_cbv.ListView):
    pass


class CreateView(ModelNameMixin, ServiceViewMixin, edit.CreateView):
    pass


class DeleteView(ModelNameMixin, ServiceViewMixin, edit.DeleteView):
    pass


class UpdateView(ModelNameMixin, ServiceViewMixin, edit.UpdateView):
    pass
