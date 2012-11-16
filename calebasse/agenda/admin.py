from django.contrib import admin

import reversion

from models import Event, EventType, Note, Occurrence

admin.site.register(Event, reversion.VersionAdmin)
admin.site.register(Occurrence, reversion.VersionAdmin)
admin.site.register(EventType, reversion.VersionAdmin)
admin.site.register(Note, reversion.VersionAdmin)
