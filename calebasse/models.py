from django.db import models
from django.contrib.localflavor.fr.forms import FRPhoneNumberField, FRZipCodeField


class PhoneNumberField(models.CharField):
    def __init__(self, **kwargs):
        kwargs['max_length'] = 20
        super(PhoneNumberField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        default = { 'form_class': FRPhoneNumberField }
        default.update(kwargs)
        return super(PhoneNumberField, self).formfield(**default)

class ZipCodeField(models.CharField):
    def __init__(self, **kwargs):
        kwargs['max_length'] = 5
        super(ZipCodeField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        default = { 'form_class': FRZipCodeField }
        default.update(kwargs)
        return super(ZipCodeField, self).formfield(**default)
