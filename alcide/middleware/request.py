# -*- coding: utf-8 -*-
import threading

if not 'context' in locals():
    context = threading.local()

def _get_context():
    return context

def get_request():
    return getattr(_get_context(), 'request', None)

def set_request(request):
    _get_context().request=request

class GlobalRequestMiddleware(object):
    def process_request(self, request):
        set_request(request)
