from django.conf.urls import patterns, url, include
from calebasse.actes.views import update_act

act_patterns = patterns('calebasse.actes.views',
        url(r'^$', 'act_listing', name='act-listing'),
        url(r'^nouvel-acte/$', 'act_new', name='act-new'),
        url(r'^(?P<pk>\d+)/update$', update_act),
)

urlpatterns = patterns('calebasse.actes.views',
        url(r'^$', 'redirect_today'),
        url(r'^(?P<date>[^/]*)/', include(act_patterns))
)
