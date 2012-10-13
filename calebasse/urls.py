from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

service_patterns = patterns('',
    url(r'^$', 'calebasse.views.homepage', name='homepage'),
    url(r'^agenda/', include('calebasse.agenda.urls')),
    url(r'^dossiers/', include('calebasse.dossier.urls')),
    url(r'^actes/', include('calebasse.acte.urls')),
    url(r'^facturation/', include('calebasse.facturation.urls')),
    url(r'^personnes/', include('calebasse.personnel.urls')),
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
    url(r'^(?P<service>[a-z-]+)/', include(service_patterns)),
)
