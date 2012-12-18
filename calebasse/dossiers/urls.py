from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import PatientRecord
from views import (patientrecord_home, patient_record, state_form,
        new_patient_record, patientrecord_delete, new_patient_contact,
        new_patient_address, delete_patient_contact, delete_patient_address,
        update_paper_id, update_patient_address, update_patient_contact,
        new_healthcare_treatment, new_healthcare_diagnostic,
        new_healthcare_notification, new_socialisation_duration,
        update_socialisation_duration, delete_socialisation_duration)
from forms import EditPatientRecordForm

urlpatterns = patterns('',
        url(r'^$', patientrecord_home),
        url(r'^new$', new_patient_record),
        url(r'^(?P<pk>\d+)/view$', patient_record),
        url(r'^(?P<pk>\d+)/delete$', patientrecord_delete),
        url(r'^(?P<pk>\d+)/update/paper_id$', update_paper_id),
        url(r'^(?P<patientrecord_id>\d+)/update-state$', state_form),
        url(r'^(?P<patientrecord_id>\d+)/address/new$', new_patient_address),
        url(r'^(?P<patientrecord_id>\d+)/address/(?P<pk>\d+)/update$', update_patient_address),
        url(r'^(?P<patientrecord_id>\d+)/address/(?P<pk>\d+)/del$', delete_patient_address),
        url(r'^(?P<patientrecord_id>\d+)/contact/new$', new_patient_contact),
        url(r'^(?P<patientrecord_id>\d+)/contact/(?P<pk>\d+)/update$', update_patient_contact),
        url(r'^(?P<patientrecord_id>\d+)/contact/(?P<pk>\d+)/del$', delete_patient_contact),
        url(r'^(?P<patientrecord_id>\d+)/healthcare_treatment/new$', new_healthcare_treatment),
        url(r'^(?P<patientrecord_id>\d+)/healthcare_diagnostic/new$', new_healthcare_diagnostic),
        url(r'^(?P<patientrecord_id>\d+)/healthcare_notification/new$', new_healthcare_notification),
        url(r'^(?P<patientrecord_id>\d+)/socialisation/new$', new_socialisation_duration),
        url(r'^(?P<patientrecord_id>\d+)/socialisation/(?P<pk>\d+)/update$', update_socialisation_duration),
        url(r'^(?P<patientrecord_id>\d+)/socialisation/(?P<pk>\d+)/del$', delete_socialisation_duration),
)
