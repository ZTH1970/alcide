from django.conf.urls import patterns, url, include
from calebasse.actes.views import update_act, rebill_act, delete_act

act_patterns = patterns('calebasse.actes.views',
        url(r'^$', 'act_listing', name='act-listing'),
        url(r'^act-new/$', 'act_new', name='act-new'),
        url(r'^(?P<pk>\d+)/update$', update_act),
        url(r'^(?P<pk>\d+)/delete$', delete_act),
        url(r'^(?P<pk>\d+)/rebill', rebill_act),
)

urlpatterns = patterns('calebasse.actes.views',
        url(r'^$', 'redirect_today'),
        url(r'^(?P<date>[^/]*)/', include(act_patterns))
)
