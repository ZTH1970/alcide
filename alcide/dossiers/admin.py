from django.contrib import admin

import reversion

from models import (CmppHealthCareDiagnostic, CmppHealthCareTreatment,
        FileState, HealthCare, PatientRecord, PatientAddress,
        PatientContact, SessadHealthCareNotification, Status)

admin.site.register(CmppHealthCareDiagnostic, reversion.VersionAdmin)
admin.site.register(CmppHealthCareTreatment, reversion.VersionAdmin)
admin.site.register(FileState, reversion.VersionAdmin)
admin.site.register(HealthCare, reversion.VersionAdmin)
admin.site.register(PatientRecord, reversion.VersionAdmin)
admin.site.register(PatientAddress, reversion.VersionAdmin)
admin.site.register(PatientContact, reversion.VersionAdmin)
admin.site.register(SessadHealthCareNotification, reversion.VersionAdmin)
admin.site.register(Status, reversion.VersionAdmin)

