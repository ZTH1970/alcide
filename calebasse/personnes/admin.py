from django.contrib import admin

from calebasse.personnes.models import Worker, TimeTable

admin.site.register(Worker)
admin.site.register(TimeTable)
