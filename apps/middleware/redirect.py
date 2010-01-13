# -*- mode: python; coding: utf-8; -*-

from lib.exceptions import RedirectException
from django.http import HttpResponseRedirect

class RedirectMiddleware(object):
    def process_request(self, request):
        try:
            future_messages = request.session['future_site_messages']
        except KeyError:
            future_messages = {'errors':[],'notices':[]}
        request.session['future_site_messages'] = {
            'errors': [],
            'notices': []}
        request.session['site_messages'] = {
            'errors': future_messages['errors'],
            'notices': future_messages['notices']}
        return None

    def process_exception(self, request, exception):
        if isinstance(exception,RedirectException):
            if exception.error_message:
                request.session['future_site_messages']['errors'].append(
                    exception.error_message)
            if exception.notice_message:
                request.session['future_site_messages']['notices'].append(
                    exception.notice_message)
            return HttpResponseRedirect(exception.redirect_uri)
