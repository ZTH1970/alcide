from django.conf.urls import patterns, url
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from models import Dossier
from forms import CreateDossierForm, EditDossierForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Dossier)),
    url(r'^nouveau/$', CreateView.as_view(model=Dossier,
        form_class=CreateDossierForm,
        template_name_suffix='_nouveau.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=Dossier,
        form_class=EditDossierForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=Dossier)),
)
