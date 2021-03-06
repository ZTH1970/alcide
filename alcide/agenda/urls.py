from django.conf.urls import url, patterns, include

from alcide.cbv import TemplateView
from django.views.decorators.csrf import csrf_exempt

from alcide.decorators import validator_only

from views import (redirect_today, AgendaHomepageView, NewAppointmentView,
        NewEventView, AgendaServiceActivityView, UpdateAppointmentView,
        UpdateEventView, AgendaServiceActValidationView, AutomatedValidationView,
        UnlockAllView, AgendasTherapeutesView, JoursNonVerrouillesView,
        AjaxWorkerTabView, AjaxRessourceTabView, AjaxDisponibilityColumnView,
        DeleteOccurrenceView, DeleteEventView, UpdatePeriodicEventView,
        UpdatePeriodicAppointmentView, PeriodicEventsView)

agenda_patterns = patterns('',
            url(r'^$',
                AgendaHomepageView.as_view(
                    template_name='agenda/index.html'),
                name='agenda'),
            url(r'^nouveau-rdv/$',
                NewAppointmentView.as_view(),
                name='nouveau-rdv'),
            url(r'^update-rdv/(?P<pk>\d+)$',
                UpdateAppointmentView.as_view(),
                name='update-rdv'),
            url(r'^update-periodic-rdv/(?P<pk>\d+)$',
                UpdatePeriodicAppointmentView.as_view(),
                name='update-periodic-rdv'),
            url(r'^new-event/$',
                NewEventView.as_view(),
                name='new-event'),
            url(r'^update-event/(?P<pk>\d+)$',
                UpdateEventView.as_view(),
                name='update-event'),
            url(r'^update-periodic-event/(?P<pk>\d+)$',
                UpdatePeriodicEventView.as_view(),
                name='update-periodic-event'),
            url(r'^delete-occurrence/(?P<pk>\d+)$',
                csrf_exempt(DeleteOccurrenceView.as_view()),
                name='delete-occurrence'),
            url(r'^delete-event/(?P<pk>\d+)$',
                csrf_exempt(DeleteEventView.as_view()),
                name='delete-event'),
            url(r'^activite-du-service/$',
                AgendaServiceActivityView.as_view(
                    template_name='agenda/service-activity.html'),
                name='activite-du-service'),
            url(r'^validation-des-actes/$',
                validator_only(AgendaServiceActValidationView.as_view(
                    template_name='agenda/act-validation.html')),
                name='validation-des-actes'),
            url(r'^validation-des-actes/validation-all/$',
                validator_only(AutomatedValidationView.as_view()),
                name='validation-all'),
            url(r'^validation-des-actes/unlock-all/$',
                validator_only(UnlockAllView.as_view()),
                name='unlock-all'),
            url(r'^agendas-therapeutes/$',
                AgendasTherapeutesView.as_view(
                    template_name='agenda/agendas-therapeutes.html'),
                name='agendas-therapeutes'),
            url(r'^jours-non-verrouilles/$',
                validator_only(JoursNonVerrouillesView.as_view(
                    template_name='agenda/days-not-locked.html')),
                name='days-not-locked'),
            url(r'^ajax-worker-tab/(?P<worker_id>\d+)$',
                AjaxWorkerTabView.as_view(),
                name='ajax-worker-tab'),
            url(r'^ajax-ressource-tab/(?P<ressource_id>\d+)$',
                AjaxRessourceTabView.as_view(),
                name='ajax-ressource-tab'),
            url(r'^disponibility/(?P<ressource_type>\w+)-(?P<ressource_id>\d+)$',
                AjaxDisponibilityColumnView.as_view(),
                name='ajax-disponibility-column'),
            url(r'^rendez-vous-periodiques/$',
                PeriodicEventsView.as_view(),
                name='periodic-events'),
            url(r'^rendez-vous-periodiques/(?P<worker_id>\d+)/$',
                PeriodicEventsView.as_view(),
                name='periodic-events-for-worker'),
            )

urlpatterns = patterns('',
        url(r'^$', redirect_today),
        url(r'^(?P<date>[^/]*)/', include(agenda_patterns)))
