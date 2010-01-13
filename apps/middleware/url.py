# -*- mode: python; coding: utf-8; -*-

"""
URL Middleware
Stefano J. Attardi (attardi.org)

$Id: url.py 203 2007-03-06 17:04:55Z asolovyov $
$URL$

Cleans up urls by adding/removing trailing slashes, adding/removing
the www. prefix, and allowing the language to be set from the url.

If APPEND_SLASH is set to False, trailing slashes are removed from the
urls, except for urls which have an explicit trailing slash in
urls.py, in which case a trailing slash is added.

If REMOVE_WWW is set to True, the www. prefix is removed.

Finally, ?lang=xx can be appended to any url to override the default
language setting. This override is remembered for the following
requests. For example, /article?lang=it would show the article in
Italian regardless of brower settings or cookies, and any following
request to the site would be shown in Italian by default.

Changelog

1.3
Only use sessions for the language preference if the session
cookie has already been set (regardless of whether session middleware
is active). Otherwise use the plain django_language cookie.
Only import the FlatPages module if it is active.

1.2
Added support for FlatPages.
Switched to Django's resolve function (with workaround for when it
returns None).

1.1
Various bugfixes.

1.0
First release.
"""
__version__ = "1.3"
__license__ = "Python"
__copyright__ = "Copyright (C) 2006, Stefano J. Attardi"
__author__ = "Stefano J. Attardi <http://attardi.org/>"
__contributors__ = ["Antonio Cavedoni <http://cavedoni.com/>"]

from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import resolve
from django.utils.translation import check_for_language
import os

class UrlMiddleware(object):

    def process_request(self, request):

        # Change the language setting for the current page
        if "lang" in request.GET and check_for_language(request.GET["lang"]):
            if hasattr(request, 'session'):
                request.session['django_language'] = request.GET["lang"]
            else:
                request.COOKIES['django_language'] = request.GET["lang"]

        # Check for a redirect based on settings.APPEND_SLASH and settings.PREPEND_WWW
        httpHost = request.META.get('HTTP_HOST', '')
        old_url = [httpHost, request.path]
        new_url = old_url[:]

        # if REMOVE_WWW is True, remove the www. from the urls if necessary
        if hasattr(settings, "REMOVE_WWW") and settings.REMOVE_WWW and old_url[0].startswith('www.'):
            new_url[0] = old_url[0][4:]

        if hasattr(settings, "APPEND_SLASH") and not settings.APPEND_SLASH:
            # if the url is not found, try with(out) the trailing slash
            if not self._urlExists(old_url[1]):

                if old_url[1][-1] == "/":
                    other = old_url[1][:-1]
                else:
                    other = old_url[1] + "/"

                if self._urlExists(other):
                    new_url[1] = other

            if new_url != old_url:
                # Redirect
                newurl = "%s://%s%s" % (os.environ.get('HTTPS') == 'on' and 'https' or 'http', new_url[0], new_url[1])
                if request.GET:
                    newurl += '?' + request.GET.urlencode()
                return HttpResponseRedirect(newurl)

        return None

    def process_response(self, request, response):

        # Change the language setting for future pages
        if "lang" in request.GET and check_for_language(request.GET["lang"]):
            if 'sessionid' in request.COOKIES:
                request.session['django_language'] = request.GET["lang"]
            else:
                response.set_cookie('django_language', request.GET["lang"])

        return response

    def _urlExists(self, path):
        try:
            if resolve(path) is None: raise Http404 # None?!? You mean 404...
            return True
        except Http404:
            # check for flatpages
            if "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware" in settings.MIDDLEWARE_CLASSES:
                from django.contrib.flatpages.models import FlatPage
                return FlatPage.objects.filter(url=path, sites__id=settings.SITE_ID).count() == 1

