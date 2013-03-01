from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from urls_utils import decorated_includes

from calebasse.api import (act_ressource, event_resource,
        patientrecord_resource, patientaddress_ressource)
from tastypie.api import Api

admin.autodiscover()

v1_api = Api(api_name="v1")
v1_api.register(act_ressource)
v1_api.register(event_resource)
v1_api.register(patientaddress_ressource)
v1_api.register(patientrecord_resource)

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

    (r'^$', 'calebasse.views.redirect_to_homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^api/',
        decorated_includes(login_required, include(v1_api.urls))),
    url(r'^(?P<service>[a-z-]+)/', decorated_includes(login_required,
        include(service_patterns))),
    url(r'^lookups/', include('ajax_select.urls')),
)

from django.conf import settings
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()


