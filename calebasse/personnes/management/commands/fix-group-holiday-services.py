from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from calebasse.personnes.models import Holiday
        from calebasse.ressources.models import Service

        all_services = list(Service.objects.all())

        for holiday in Holiday.objects.filter(services__isnull=True):
            for service in all_services:
                holiday.services.add(service)
