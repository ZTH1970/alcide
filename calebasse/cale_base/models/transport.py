
from django.db import models

class Transport(models.Model):

    class Meta:
        app_label = 'cale_base'

    company = models.ForeignKey('TransportCompany')
    transport_type = models.ForeignKey('TransportType')


class TransportCompany(models.Model):

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zip_code = models.IntegerField(max_length=6)
    city = models.CharField(max_length=80)
    phone = models.CharField(max_length=25)
    email = models.EmailField()
    contact_name = models.CharField(max_length=80)

class TransportType(models.Model):

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=100)


