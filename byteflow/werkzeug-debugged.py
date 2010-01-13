#!/usr/bin/env python
import os
import sys

from werkzeug import run_simple, DebuggedApplication
from django.views import debug
from django.core.handlers.wsgi import WSGIHandler

def null_technical_500_response(request, exc_type, exc_value, tb):
    raise exc_type, exc_value, tb
debug.technical_500_response = null_technical_500_response

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except (ValueError, IndexError):
        port = 8000
    run_simple('0.0.0.0', port, DebuggedApplication(WSGIHandler(), True), True)
