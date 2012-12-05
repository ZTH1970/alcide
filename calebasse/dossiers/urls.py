from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import PatientRecord
from views import (patientrecord_home, patient_record, state_form,
        new_patient_record, patientrecord_delete, new_patient_contact,
        new_patient_address)
from forms import EditPatientRecordForm

urlpatterns = patterns('',
        url(r'^$', patientrecord_home),
        url(r'^new$', new_patient_record),
        url(r'^(?P<pk>\d+)/view$', patient_record),
        url(r'^(?P<pk>\d+)/delete$', patientrecord_delete),
        url(r'^(?P<pk>\d+)/new-contact$', new_patient_contact),
        url(r'^(?P<pk>\d+)/new-address$', new_patient_address),
        url(r'^(?P<pk>\d+)/update-state$', state_form),
)
