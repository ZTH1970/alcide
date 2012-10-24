from django.conf.urls import url, patterns, include

from calebasse.cbv import TemplateView, CreateView
from calebasse.actes.models import EventAct

from views import redirect_today, AgendaHomepageView
from forms import NewAppointmentForm


agenda_patterns = patterns('',
            url(r'^$',
                AgendaHomepageView.as_view(
                    template_name='agenda/index.html'),
                name='agenda'),
            url(r'^nouveau-rdv/$',
                CreateView.as_view(model=EventAct,
                    form_class=NewAppointmentForm,
                    template_name='agenda/nouveau-rdv.html'),
                name='nouveau-rdv'),
            url(r'^activite-du-service/$',
                TemplateView.as_view(
                    template_name='agenda/activite-du-service.html'),
                name='activite-du-service'),
            url(r'^validation-des-actes/$',
                TemplateView.as_view(
                    template_name='agenda/validation-des-actes.html'),
                name='validation-des-actes'),
            url(r'^rendez-vous-periodiques/$',
                TemplateView.as_view(
                    template_name='agenda/rendez-vous-periodique.html'),
                name='rendez-vous-periodiques'),
            )

urlpatterns = patterns('',
        url(r'^$', redirect_today),
        url(r'^(?P<date>[^/]*)/', include(agenda_patterns)))

