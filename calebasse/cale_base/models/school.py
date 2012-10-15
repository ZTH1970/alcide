
from django.db import models

class School(models.Model):

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=70, blank=False)
    description = models.CharField(max_length=200)
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120, blank=True, null=True, default=None)
    zip_code = models.IntegerField(max_length=8)
    city = models.CharField(max_length=80)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    principal_name = models.CharField(max_length=70)

