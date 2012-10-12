from django.forms import ModelForm

from models import Acte

class CreateActeForm(ModelForm):
    class Meta:
        model = Acte


class EditActeForm(ModelForm):
    class Meta:
        model = Acte
