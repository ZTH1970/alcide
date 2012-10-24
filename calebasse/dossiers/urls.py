from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import PatientRecord
from forms import CreatePatientRecordForm, EditPatientRecordForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=PatientRecord)),
    url(r'^new/$', CreateView.as_view(model=PatientRecord,
        form_class=CreatePatientRecordForm,
        template_name_suffix='_new')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=PatientRecord,
        form_class=EditPatientRecordForm,
        template_name_suffix='_edit')),
    url(r'^(?P<pk>\d+)/delete/$', DeleteView.as_view(model=PatientRecord)),
)
