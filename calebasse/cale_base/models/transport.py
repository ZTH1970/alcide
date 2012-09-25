
from django.db import models

class Transport(models.Model):

    class Meta:
        app_label = 'cale_base'

    company = models.ForeignKey('TransportCompany')
    transport_type = models.ForeignKey('TransportType')


class TransportCompany(models.Model):

    class Meta:
        app_label = 'cale_base'

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=80)
    phone = models.CharField(max_length=25)


class TransportType(models.Model):

    class Meta:
        app_label = 'cale_base'

    name = models.CharField(max_length=100)


