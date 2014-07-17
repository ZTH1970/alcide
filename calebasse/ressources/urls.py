from django.conf.urls import patterns, include, url

from calebasse.ressources.views import update_school_view, new_school_view

ressource_patterns = patterns('calebasse.ressources.views',
    url(r'^$', 'list_view', name='ressource-list'),
    url(r'^new/$', 'create_view', name='ressource-create'), 
    url(r'^(?P<pk>\d+)/$', 'update_view', name='ressource-edit'),
    url(r'^(?P<pk>\d+)/delete/$', 'delete_view', name='ressource-delete'),
)

urlpatterns = patterns('',
    url(r'^school/(?P<pk>\d+)/$', update_school_view),
    url(r'^school/new/$', new_school_view),
    url(r'^(?P<model_name>[a-z-]*)/', include(ressource_patterns)),
    url(r'^$', 'calebasse.ressources.views.homepage',
        name='ressource-homepage'),
    )


