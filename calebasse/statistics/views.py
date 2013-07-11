# -*- coding: utf-8 -*-
from calebasse.cbv import TemplateView

class StatisticsHomepageView(TemplateView):

    template_name = 'statistics/index.html'

    def get_context_data(self, **kwargs):
        context = super(StatisticsHomepageView, self).get_context_data(**kwargs)
        context['statistics'] = list()
        return context
