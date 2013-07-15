from django.conf.urls import patterns, include, url

from views import StatisticsHomepageView

statistics_patterns = patterns('calebasse.statistics.views', )

urlpatterns = patterns('',
    url(r'^(?P<model_name>[a-z-]*)/', include(statistics_patterns)),
    url(r'^$', StatisticsHomepageView.as_view()),
    )
