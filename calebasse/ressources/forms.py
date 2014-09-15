
from calebasse.ressources.models import School
from django.forms import ModelForm

class SchoolForm(ModelForm):
    class Meta:
        model = School
        exclude = ('display_name',)
