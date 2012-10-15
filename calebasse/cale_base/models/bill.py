
from django.db import models


class Bill(models.Model):

    class Meta:
        app_label = 'cale_base'

    number = models.CharField(max_length=20)
    patient = models.ForeignKey('Patient')
    organization = models.ForeignKey('Organization')
    fund = models.ForeignKey('Fund')
    date = models.DateField()
    acts = models.ManyToManyField('Act')

class Fund(models.Model):
    """ Funds like CPAM
    """

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=80)
    abbreviation = models.CharField(max_length=8)
    active = models.BooleanField(default=True)
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120, blank=True, null=True, default=None)
    zip_code = models.IntegerField(max_length=8)
    city = models.CharField(max_length=80)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    accounting_number = models.CharField(max_length=30)
    correspondant = models.CharField(max_length=80)
    # TODO : add fields : tp, caisse, centre, istrans, banque_id
