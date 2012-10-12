
from django.db import models

class Service(models.Model):

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=100)

