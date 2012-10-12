from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

service_patterns = patterns('',
    url(r'^agenda/', include('calebasse.agenda.urls')),
    url(r'^dossier/', include('calebasse.dossier.urls')),
    url(r'^acte/', include('calebasse.acte.urls')),
    url(r'^facturation/', include('calebasse.facturation.urls')),
    url(r'^personnel/', include('calebasse.personnel.urls')),
    url(r'^ressources/', include('calebasse.ressources.urls')),
)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'calebasse.views.home', name='home'),
    # url(r'^calebasse/', include('aps42.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<service>[a-z-]+)/', include(service_patterns)),

)
