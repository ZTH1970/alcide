
from calebasse import agenda
from dateutil import rrule
from django.contrib.auth.models import User
from django.template import Context, Template
from django.shortcuts import render

    #owners=User.objects.all()
    #agenda.models.create_event('rdv 42', ('rdv', 'Rendez-vous'),
    #        owners=owners, freq=rrule.MONTHLY)

def index(request, *args, **kwargs):

    context = {}
    template='index.html'
    return render(request, template, context)


