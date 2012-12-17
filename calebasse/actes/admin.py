from django.contrib import admin

import reversion

from models import Act, ActValidationState

admin.site.register(Act, reversion.VersionAdmin)
admin.site.register(ActValidationState, reversion.VersionAdmin)
