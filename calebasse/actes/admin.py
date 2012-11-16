from django.contrib import admin

import reversion

from models import Act, ActValidationState, EventAct

admin.site.register(Act, reversion.VersionAdmin)
admin.site.register(ActValidationState, reversion.VersionAdmin)
admin.site.register(EventAct, reversion.VersionAdmin)
