# -*- mode: python; coding: utf-8; -*-

"""
AJAX Middleware

Catches common errors in AJAX views.
"""

from lib.http import JsonResponse
from lib.exceptions import *

class AjaxMiddleware(object):

    def process_exception(self, request, exception):
        if not isinstance(exception, AjaxException):
            return None
        if isinstance(exception, AjaxDataException):
            return JsonResponse(exception.data)
        if isinstance(exception, Ajax404):
            return JsonResponse({'error': {'type': 404, 'message': exception.message}})
