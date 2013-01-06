from datetime import date, timedelta, datetime, time
from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success
from django.db.models import Q
from ... import models
from ....actes.models import Act

class Command(BaseCommand):
    help = 'Create acts for events in the following days'

    @commit_on_success
    def handle(self, *args, **options):
        today = date.today()
        print 'on', today
        qs = models.EventWithAct.objects.filter(
                Q(recurrence_periodicity__isnull=False, recurrence_end_date__isnull=True) |
                Q(recurrence_periodicity__isnull=False, recurrence_end_date__gte=today) |
                Q(start_datetime__gte=datetime.combine(today, time.min)))
        print 'handling', qs.count(), 'active events'
        before = Act.objects.count()
        for event in qs:
            event.save()
        count = Act.objects.count()-before
        print 'created', count , 'acts'
