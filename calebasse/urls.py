from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from urls_utils import decorated_includes

from calebasse.api import EventResource, OccurrenceResource

admin.autodiscover()

event_resource = EventResource()
occurrence_resource = OccurrenceResource()

service_patterns = patterns('',
    url(r'^$', 'calebasse.views.homepage', name='homepage'),
    url(r'^agenda/', include('calebasse.agenda.urls')),
    url(r'^dossiers/', include('calebasse.dossiers.urls')),
    url(r'^actes/', include('calebasse.actes.urls')),
    url(r'^facturation/', include('calebasse.facturation.urls')),
    url(r'^personnes/', include('calebasse.personnes.urls')),
    url(r'^ressources/', include('calebasse.ressources.urls')),
)

urlpatterns = patterns('',
    # Examples:
    # url(r'^calebasse/', include('aps42.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^$', redirect_to, { 'url': '/cmpp/' }),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^api/',
        decorated_includes(login_required, include(event_resource.urls))),
    url(r'^api/',
        decorated_includes(login_required, include(occurrence_resource.urls)),
        ),
    url(r'^(?P<service>[a-z-]+)/', decorated_includes(login_required,
        include(service_patterns))),
    url(r'^lookups/', include('ajax_select.urls')),
)
