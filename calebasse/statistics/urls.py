from django.conf.urls import patterns, include, url

from views import StatisticsHomepageView, StatisticsFormView, StatisticsDetailView

urlpatterns = patterns('',
    url(r'^$', StatisticsHomepageView.as_view()),
    url(r'^detail/(?P<name>\w{1,50})/$', view=StatisticsDetailView.as_view()),
    url(r'^form/(?P<name>\w{1,50})/$', view=StatisticsFormView.as_view()),
)
