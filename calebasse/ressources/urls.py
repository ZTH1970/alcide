from django.conf.urls import patterns, include, url

ressource_patterns = patterns('calebasse.ressources.views',
    url(r'^$', 'list_view', name='ressource-list'),
    url(r'^new/$', 'create_view', name='ressource-create'), 
    url(r'^(?P<pk>\d+)/$', 'update_view', name='ressource-edit'),
    url(r'^(?P<pk>\d+)/delete/$', 'delete_view', name='ressource-delete'),
)

urlpatterns = patterns('',
    url(r'^(?P<model_name>[a-z-]*)/', include(ressource_patterns)),
    url(r'^$', 'calebasse.ressources.views.homepage',
        name='ressource-homepage'),
    )


