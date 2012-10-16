from django.forms import ModelForm

from models import Facture

class CreateFactureForm(ModelForm):
    class Meta:
        model = Facture


class EditFactureForm(ModelForm):
    class Meta:
        model = Facture
