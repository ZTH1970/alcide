from django.conf.urls import patterns, url

from views import (FacturationHomepageView, FacturationDetailView,
    ValidationFacturationView, close_form)

urlpatterns = patterns('calebasse.facturation.views',
    url(r'^$', FacturationHomepageView.as_view()),
    url(r'^(?P<pk>\d+)/$', FacturationDetailView.as_view()),
    url(r'^(?P<pk>\d+)/validate/$',
        ValidationFacturationView.as_view(),
        name='validate-facturation'),
    url(r'^(?P<pk>\d+)/clore$', close_form),
)
