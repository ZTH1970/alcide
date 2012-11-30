from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import PatientRecord
from views import (patientrecord_home, patient_record, state_form,
        new_patient_record, FinaccueilPatientRecordView)
from forms import EditPatientRecordForm

urlpatterns = patterns('',
        url(r'^$', patientrecord_home),
        url(r'^(?P<pk>\d+)/view$', patient_record),
        url(r'^new$', new_patient_record),
        url(r'^(?P<pk>\d+)/update-state$', state_form),
        url(r'^(?P<pk>\d+)/finaccueil-patientrecord/$',
            FinaccueilPatientRecordView.as_view(),
            name='finaccueil-patientrecord'),
)
