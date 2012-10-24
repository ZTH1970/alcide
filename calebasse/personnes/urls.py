from django.conf.urls import patterns, url, include
from calebasse.cbv import (ListView, CreateView, DeleteView, UpdateView,
        TemplateView)

from django.contrib.auth.models import User
from models import Worker
from forms import CreateUserForm, EditUserForm
from forms import CreatePersonnelForm, EditPersonnelForm
#from forms import CreateCongeAnnuelForm, EditCongeAnnuelForm

acces_patterns = patterns('',
    url(r'^$', ListView.as_view(model=User)),
    url(r'^nouveau/$', CreateView.as_view(model=User,
        form_class=CreateUserForm,
        template_name_suffix='_new.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=User,
        form_class=EditUserForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/delete/$', DeleteView.as_view(model=User)),
)


personne_patterns = patterns('',
    url(r'^$', ListView.as_view(model=Worker)),
    url(r'^new/$', CreateView.as_view(model=Worker,
        form_class=CreatePersonnelForm,
        template_name_suffix='_new.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=Worker,
        form_class=EditPersonnelForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/delete/$', DeleteView.as_view(model=Worker)),
)


#conges_annuels_patterns = patterns('',
#    url(r'^$', ListView.as_view(model=CongeAnnuel)),
#    url(r'^nouveau/$', CreateView.as_view(model=CongeAnnuel,
#        form_class=CreateCongeAnnuelForm,
#        template_name_suffix='_nouveau.html')),
#    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=CongeAnnuel,
#        form_class=EditCongeAnnuelForm,
#        template_name_suffix='_edit.html')),
#    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=CongeAnnuel)),
#)

#conges_patterns = patterns('',
#    url(r'^$', ListView.as_view(model=Conge)),
#    url(r'^conges-annuels/', include(conges_annuels_patterns)),
#)

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='personnes/index.html')),
    url(r'^acces/', include(acces_patterns)),
    url(r'^gestion/', include(personne_patterns)),
    url(r'^conges/', include(personne_patterns)),
    )
