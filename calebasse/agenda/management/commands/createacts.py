from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success
from ... import models
from ....actes.models import Act

class Command(BaseCommand):
    help = 'Create acts for events in the following days'

    @commit_on_success
    def handle(self, *args, **options):
        i = date.today()
        end = i + timedelta(days=90)
        total = 0
        while i != end:
            print 'on', i,
            before = Act.objects.count()
            qs = models.EventWithAct.objects.for_today(i)
            print qs.count(), 'events',
            for e in qs:
                e.save()
            count = Act.objects.count()-before
            total += count
            print 'created', count , 'acts'
            i += timedelta(days=1)
        print 'total:', total, 'acts'
