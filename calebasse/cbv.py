from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.views.generic import list as list_cbv, edit, base # ListView
# from django.views.generic.edit import # CreateView, DeleteView, UpdateView

from views import SERVICES_MAP


class ServiceViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ServiceViewMixin, self).get_context_data(**kwargs)
        if self.request.GET.get('popup'):
            context['popup'] = True
        context['service'] = self.kwargs.get('service')
        context['service_name'] = SERVICES_MAP.get(context['service'])
        if 'date' in self.kwargs:
            day = datetime.strptime(self.kwargs.get('date'),
                    '%Y-%m-%d').date()
            context['date'] = day
            context['previous_day'] = day + relativedelta(days=-1)
            context['next_day'] = day + relativedelta(days=1)
            context['previous_month'] = day + relativedelta(months=-1)
            context['next_month'] = day + relativedelta(months=1)
        return context

class TemplateView(ServiceViewMixin, base.TemplateView):
    pass

class ListView(ServiceViewMixin, list_cbv.ListView):
    pass

class CreateView(ServiceViewMixin, edit.CreateView):
    pass

class DeleteView(ServiceViewMixin, edit.DeleteView):
    pass

class UpdateView(ServiceViewMixin, edit.UpdateView):
    pass
