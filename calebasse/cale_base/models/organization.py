
from django.db import models

class Place(models.Model):

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=40, blank=False)
    address = models.CharField(max_length=120)
    address_complement = models.CharField(max_length=120, blank=True, null=True, default=None)
    zip_code = models.IntegerField(max_length=6)
    city = models.CharField(max_length=80)

class OrganizationAnnex(models.Model):

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=40, blank=False)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    services = models.ForeignKey('Service')

class Organization(models.Model):

    class Meta:
        app_label = 'cale_base'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=40, blank=False)
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    services = models.ForeignKey('Service')
    # TODO: add this fields : finess, suite, dm, dpa, genre, categorie, statut_juridique, mft, mt, dmt

