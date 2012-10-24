from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import PatientRecord
from forms import CreateDossierForm, EditDossierForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=PatientRecord)),
    url(r'^new/$', CreateView.as_view(model=PatientRecord,
        form_class=CreateDossierForm,
        template_name_suffix='_new.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=PatientRecord,
        form_class=EditDossierForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=PatientRecord)),
)
