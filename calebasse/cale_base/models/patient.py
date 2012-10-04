
from django.db import models

class Patient(models.Model):

    class Meta:
        app_label = 'cale_base'

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    # TODO add other fields




