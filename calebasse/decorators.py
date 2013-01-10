from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from functools import wraps

from utils import is_super_user, is_validator

auth_url = '/accounts/login/'


'''
''''''
    Decorators to protect views
''''''
'''

def super_user_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not is_super_user(request.user):
            return HttpResponseRedirect(auth_url)
        return view_func(request, *args, **kwargs)
    return login_required(wraps(view_func)(_wrapped_view))

def validator_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not is_validator(request.user):
            return HttpResponseRedirect(auth_url)
        return view_func(request, *args, **kwargs)
    return login_required(wraps(view_func)(_wrapped_view))
