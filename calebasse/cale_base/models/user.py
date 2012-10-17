
from django.db import models
from django.contrib.auth.models import User

from calebasse.exceptions import CalebasseException
from calebasse.agenda import managers
from dateutil import rrule

class CalebasseUser(models.Model):

    class Meta:
        app_label = 'cale_base'

    user = models.OneToOneField(User)
    services = models.ManyToManyField('ActType')
    work_event = models.ManyToManyField('agenda.Event', related_name='work_events')
    holidays = models.ManyToManyField('agenda.Event', related_name='holidays')

