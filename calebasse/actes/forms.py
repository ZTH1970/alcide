from django.forms import ModelForm

from models import Act

class CreateActForm(ModelForm):
    class Meta:
        model = Act


class EditActForm(ModelForm):
    class Meta:
        model = Act
