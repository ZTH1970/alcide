from django.contrib import admin

import reversion

from calebasse.facturation.models import Invoicing

admin.site.register(Invoicing, reversion.VersionAdmin)
