
from calebasse import agenda
from dateutil import rrule
from django.contrib.auth.models import User

def test(request, *args, **kwargs):
    """docstring for test"""
    owners=User.objects.all()
    agenda.models.create_event('rdv 42', ('rdv', 'Rendez-vous'),
            owners=owners, freq=rrule.MONTHLY)


