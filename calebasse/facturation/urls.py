from django.conf.urls import patterns, url

from views import (FacturationHomepageView, FacturationDetailView,
    CloseFacturationView)

urlpatterns = patterns('calebasse.facturation.views',
    url(r'^$', FacturationHomepageView.as_view()),
    url(r'^(?P<pk>\d+)/$', FacturationDetailView.as_view()),
    url(r'^(?P<pk>\d+)/clore/$',
        CloseFacturationView.as_view(),
        name='close-facturation'),
)
