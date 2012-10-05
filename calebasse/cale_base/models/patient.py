
from django.db import models

class Patient(models.Model):

    class Meta:
        app_label = 'cale_base'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # TODO add other fields




