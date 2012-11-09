from django.conf.urls import patterns, url, include


user_patterns = patterns('calebasse.personnes.views',
    url(r'^$', 'user_listing'),
    url(r'^new/$', 'user_new'),
    url(r'^(?P<pk>\d+)/$', 'user_update'),
    url(r'^(?P<pk>\d+)/delete/$', 'user_delete'),
)


worker_patterns = patterns('calebasse.personnes.views',
    url(r'^$', 'worker_listing'),
    url(r'^new/$', 'worker_new'),
    url(r'^(?P<pk>\d+)/$', 'worker_update'),
    url(r'^(?P<pk>\d+)/delete/$', 'worker_delete'),
)


urlpatterns = patterns('calebasse.personnes.views',
    url(r'^$', 'homepage'),
    url(r'^acces/', include(user_patterns)),
    url(r'^gestion/', include(worker_patterns)),
    )
