
from django.db import models
from django.contrib.auth.models import User

class CalebasseUser(User):

    class Meta:
        app_label = 'cale_base'

    services = models.ManyToManyField('ActType')
