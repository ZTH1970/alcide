from django.contrib import admin

import reversion

from calebasse.facturation.models import Invoicing, PricePerAct

admin.site.register(Invoicing, reversion.VersionAdmin)
admin.site.register(PricePerAct, reversion.VersionAdmin)
