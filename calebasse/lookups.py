
from ajax_select import LookupChannel

class CalebasseLookup(LookupChannel):

    def check_auth(self,request):
        if not request.user.is_authenticated():
            raise PermissionDenied

