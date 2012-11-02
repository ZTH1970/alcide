from django.conf.urls import url, patterns, include

from calebasse.cbv import TemplateView

from views import (redirect_today, AgendaHomepageView, NewAppointmentView,
        NewEventView, AgendaServiceActivityView)


agenda_patterns = patterns('',
            url(r'^$',
                AgendaHomepageView.as_view(
                    template_name='agenda/index.html'),
                name='agenda'),
            url(r'^nouveau-rdv/$',
                NewAppointmentView.as_view(),
                name='nouveau-rdv'),
            url(r'^new-event/$',
                NewEventView.as_view(),
                name='new-event'),
            url(r'^activite-du-service/$',
                AgendaServiceActivityView.as_view(
                    template_name='agenda/service-activity.html'),
                name='activite-du-service'),
            url(r'^validation-des-actes/$',
                TemplateView.as_view(
                    template_name='agenda/act-validation.html'),
                name='validation-des-actes'),
            url(r'^rendez-vous-periodiques/$',
                TemplateView.as_view(
                    template_name='agenda/rendez-vous-periodique.html'),
                name='rendez-vous-periodiques'),
            )

urlpatterns = patterns('',
        url(r'^$', redirect_today),
        url(r'^(?P<date>[^/]*)/', include(agenda_patterns)))

