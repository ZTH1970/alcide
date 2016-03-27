# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter
def is_worker_in_service(worker, service_name):
    for service in worker.services.all():
        if service.name == service_name:
            return True
    return False


@register.filter
def is_intervenant(worker):
    return worker.type.intervene


@register.filter
def str_length_lt(value, arg):
    value = str(value)
    return len(value) < int(arg)

@register.filter
def trunc_act_type(value):
    value = value.replace('PSYCHOMOTRICITE', 'PSYCHOMOT.')
    value = value.replace('PSYCHOMOTRICITÉ', 'PSYCHOMOT.')
    value = value.replace('GROUPE', 'GR.')
    value = value.replace('BILAN', 'BIL.')
    value = value.replace('THERAPIE', 'THER.')
    value = value.replace('THÉRAPIE', 'THER.')
    if len(value) > 24:
        return value[:24] + '.'
    return value
