from django.contrib.auth.models import Group
from django.conf import settings

from datetime import timedelta, datetime

from .middleware.request import get_request

__EPOCH = datetime(day=5,month=1,year=1970)

def __date_to_datetime(date):
    return datetime(date.year, date.month, date.day)

def weeks_since_epoch(date):
    days_since_epoch = (__date_to_datetime(date) - __EPOCH).days
    return days_since_epoch // 7

def weekday_ranks(date):
    '''Returns n so that if date occurs on a certain weekday, this is the
       n-th weekday of the month counting from the first. Also return -n-1 if
       this is the n-th weekday of the month counting from the last.
    '''
    n = 0
    month = date.month
    i = date - timedelta(days=7)
    while i.month == month:
        n += 1
        i = i - timedelta(days=7)
    m = -1
    i = date + timedelta(days=7)
    while i.month == month:
        m -= 1
        i = i + timedelta(days=7)
    return n, m

def is_super_user(user):
    if not user or not user.is_authenticated():
        return False
    if user.is_superuser:
        return True
    super_group = None
    try:
        super_group = Group.objects.get(name='Super utilisateurs')
    except:
        return False
    if super_group in user.groups.all():
        return True
    return False

def is_validator(user):
    if is_super_user(user):
        return True
    if not user or not user.is_authenticated():
        return False
    validator_group = None
    try:
        validator_group = Group.objects.get(name='Administratifs')
    except:
        return False
    if validator_group in user.groups.all():
        return True
    return False

def get_nir_control_key(nir):
    try:
        # Corse dpt 2A et 2B
        minus = 0
        if nir[6] in ('A', 'a'):
            nir = [c for c in nir]
            nir[6] = '0'
            nir = ''.join(nir)
            minus = 1000000
        elif nir[6] in ('B', 'b'):
            nir = [c for c in nir]
            nir[6] = '0'
            nir = ''.join(nir)
            minus = 2000000
        nir = int(nir) - minus
        return (97 - (nir % 97))
    except:
        return None

def get_service_setting(setting_name, default_value=None):
    from .cbv import HOME_SERVICE_COOKIE
    request = get_request()
    if not request:
        return None
    service = request.COOKIES.get(HOME_SERVICE_COOKIE)
    if not service:
        return None
    if not hasattr(settings, 'SERVICE_SETTINGS'):
        return None
    return settings.SERVICE_SETTINGS.get(service, {}).get(setting_name) or default_value
