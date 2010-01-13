# -*- mode: python; coding: utf-8; -*-

import sys
from cStringIO import StringIO

from django.conf import settings

class ProfilerMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'prof' in request.GET:
            import cProfile
            self.profiler = cProfile.Profile()
            return self.profiler.runcall(callback, request, *callback_args, **callback_kwargs)

    def process_response(self, request, response):
        if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'prof' in request.GET:
            self.profiler.create_stats()
            out = StringIO()
            old_stdout, sys.stdout = sys.stdout, out
            self.profiler.print_stats(1)
            sys.stdout = old_stdout
            response.content = '<pre>%s</pre>' % out.getvalue()
        return response

