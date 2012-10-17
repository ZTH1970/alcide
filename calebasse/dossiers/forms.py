from django.forms import ModelForm

from models import PatientRecord

class CreateDossierForm(ModelForm):
    class Meta:
        model = PatientRecord


class EditDossierForm(ModelForm):
    class Meta:
        model = PatientRecord
