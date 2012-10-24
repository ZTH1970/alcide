from django.forms import ModelForm

from models import PatientRecord

class CreatePatientRecordForm(ModelForm):
    class Meta:
        model = PatientRecord


class EditPatientRecordForm(ModelForm):
    class Meta:
        model = PatientRecord
