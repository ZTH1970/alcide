
from django.db import models

class Service(models.Model):

    class Meta:
        app_label = 'cale_base'

    name = models.CharField(max_length=100)
    # TODO : add other fields

