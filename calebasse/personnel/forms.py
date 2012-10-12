from django.forms import ModelForm

from django.contrib.auth.models import User
from models import Personnel, CongeAnnuel

class CreateUserForm(ModelForm):
    class Meta:
        model = User


class EditUserForm(ModelForm):
    class Meta:
        model = User

class CreatePersonnelForm(ModelForm):
    class Meta:
        model = Personnel


class EditPersonnelForm(ModelForm):
    class Meta:
        model = Personnel

class CreateCongeAnnuelForm(ModelForm):
    class Meta:
        model = CongeAnnuel


class EditCongeAnnuelForm(ModelForm):
    class Meta:
        model = CongeAnnuel
