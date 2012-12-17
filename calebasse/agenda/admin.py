from django.contrib import admin

import reversion

from models import Event, EventType, EventWithAct

admin.site.register(Event, reversion.VersionAdmin)
admin.site.register(EventType, reversion.VersionAdmin)
admin.site.register(EventWithAct, reversion.VersionAdmin)
