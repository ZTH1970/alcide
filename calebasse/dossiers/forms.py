from django.forms import ModelForm

from models import Dossier

class CreateDossierForm(ModelForm):
    class Meta:
        model = Dossier


class EditDossierForm(ModelForm):
    class Meta:
        model = Dossier
