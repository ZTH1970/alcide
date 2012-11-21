# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import fields
from django import forms
from django.contrib.localflavor.fr.forms import FRPhoneNumberField, FRZipCodeField
from django.utils.text import capfirst


class BaseModelMixin(object):
    def __repr__(self):
        return '<%s %s %r>' % (self.__class__.__name__, self.id, unicode(self))


class PhoneNumberField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
        super(PhoneNumberField, self).__init__(*args,**kwargs)

    def formfield(self, **kwargs):
        default = { 'form_class': FRPhoneNumberField }
        default.update(kwargs)
        return super(PhoneNumberField, self).formfield(**kwargs)


class ZipCodeField(models.CharField):
    def __init__(self, **kwargs):
        kwargs['max_length'] = 5
        super(ZipCodeField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        default = { 'form_class': FRZipCodeField }
        default.update(kwargs)
        return super(ZipCodeField, self).formfield(**kwargs)

class WeekRankField(models.PositiveIntegerField):
    '''Map a list of integers to its encoding as a binary number'''
    __metaclass__ = models.SubfieldBase

    def __init__(self, **kwargs):
        kwargs['blank'] = True
        kwargs['null'] = True
        super(WeekRankField, self).__init__(**kwargs)

    def to_python(self, value):
        if isinstance(value, list):
            if value:
                try:
                    value = map(int, value)
                except ValueError:
                    raise forms.ValidationError('value must be a sequence of value coercible to integers')
                if any((i < 0 or i > 4 for i in value)):
                    raise forms.ValidationError('value must be a list of integers between 0 and 4')
                return map(int, set(value))
            else:
                return None
        value = super(WeekRankField, self).to_python(value)
        if value is None:
            return None
        try:
            value = int(value)
        except ValueError:
            raise forms.ValidationError('value must be convertible to an integer')
        if value < 0 or value >= 64:
            raise forms.ValidationError('value must be between 0 and 64')
        return tuple((i for i in range(0, 5) if (1 << i) & value))


    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors
        from to_python and validate are propagated. The correct value is
        returned if no error is raised.
        """
        value = self.to_python(value)
        [self.validate(v, model_instance) for v in value]
        self.run_validators(value)
        return value


    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ('exact', 'in'):
            s = set(((1 << v) | i for v in value for i in range(0, 64)))
            return s
        elif lookup_type == 'range':
            value = sorted(value)
            return set(((1 << v) | i for v in range(value[0], value[1]) for i in range(0, 64)))
        else:
            return fields.Field.get_prep_lookup(self, lookup_type, value)


    def get_prep_value(self, value):
        if value:
            x = sum((1 << int(i) for i in value))
            return x
        else:
            return None

    def formfield(self, **kwargs):
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name), 
                    'help_text': self.help_text, 'choices': self.get_choices(include_blank=False)}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return forms.MultipleChoiceField(**defaults)
