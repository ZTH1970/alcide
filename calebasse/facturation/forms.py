from django.forms import ModelForm

from models import Facturation

class CreateFacturationForm(ModelForm):
    class Meta:
        model = Facturation


class EditFacturationForm(ModelForm):
    class Meta:
        model = Facturation
