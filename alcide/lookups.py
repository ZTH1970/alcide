
from ajax_select import LookupChannel
from django.core.exceptions import PermissionDenied

class CalebasseLookup(LookupChannel):

    def check_auth(self, request):
        if not request.user.is_authenticated():
            raise PermissionDenied

