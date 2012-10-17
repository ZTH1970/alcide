# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.localflavor.fr.forms import FRPhoneNumberField, FRZipCodeField

WEEKDAYS = (u'lundi', u'mardi', u'mercredi', u'jeudi', u'vendredi')

class BaseModelMixin(object):
    def __repr__(self):
        return '<%s %s %r>' % (self.__class__.__name__, self.id, unicode(self))


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



class WeekdayField(models.CharField):
    WEEKDAYS_CHOICE = ((None, u'Aucun'),) \
            + tuple(zip(WEEKDAYS, map(unicode.title, WEEKDAYS)))

    def __init__(self, **kwargs):
        kwargs['max_length'] = 16
        kwargs['choices'] = self.WEEKDAYS_CHOICE
        super(WeekdayField, self).__init__(**kwargs)
