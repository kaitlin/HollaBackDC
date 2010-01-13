from django.http import HttpResponsePermanentRedirect

from revcanonical.utils import decode


def canonical_redirect(request, addr):
    obj = decode(addr)
    return HttpResponsePermanentRedirect(obj.get_absolute_url())
