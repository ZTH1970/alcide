
from django.db import models


class Bill(models.Model):

    class Meta:
        app_label = 'cale_base'

    acts = models.ManyToManyField('Act')
