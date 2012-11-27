from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import PatientRecord
from views import (PatientRecordsHomepageView, PatientRecordView,
                    patient_record)
from forms import EditPatientRecordForm

urlpatterns = patterns('',
        url(r'^$', PatientRecordsHomepageView.as_view()),
        url(r'^view/(?P<pk>\d+)/$', patient_record),
)

#    url(r'^new/$', CreateView.as_view(model=PatientRecord,
#        form_class=CreatePatientRecordForm,
#        template_name_suffix='_new')),
#    url(r'^(?P<pk>\d+)/delete/$', DeleteView.as_view(model=PatientRecord)),
#)
