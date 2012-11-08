from django.db.models import Q
from django.contrib.auth.models import User

from calebasse.cbv import ListView, UpdateView

import forms


FILTER_CRITERIA = (
        'username',
        'first_name',
        'last_name',
        'email',
        'userworker__worker__display_name',
)


class AccessView(ListView):
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

class AccessUpdateView(UpdateView):
    model = User
    template_name = 'personnes/acces-update.html'
    form_class = forms.UserForm
