from django.contrib import admin

import reversion

from calebasse.personnes.models import (Holiday, People, TimeTable,
        SchoolTeacher, UserWorker, Worker, ExternalWorker,
        ExternalTherapist, Role)

admin.site.register(Holiday, reversion.VersionAdmin)
admin.site.register(People, reversion.VersionAdmin)
admin.site.register(TimeTable, reversion.VersionAdmin)
admin.site.register(SchoolTeacher, reversion.VersionAdmin)
admin.site.register(UserWorker, reversion.VersionAdmin)
admin.site.register(Worker, reversion.VersionAdmin)
admin.site.register(ExternalWorker, reversion.VersionAdmin)
admin.site.register(ExternalTherapist, reversion.VersionAdmin)
admin.site.register(Role, reversion.VersionAdmin)
