#Based on Djangoid by Nicolas Trangez <ikke nicolast be>
# (c) Leschinsky Oleg <helge@leschinsky.in.ua>

import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.models import Site
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User as DjangoUser
from openid.server import server

from lib.decorators import render_to
from lib.helpers import reverse

from models import DjangoidUser, TrustedRoot
from djangoidstore import DjangoidStore

def get_server():
    url = 'http://%s%s' % (Site.objects.get_current().domain,
                           reverse('openid_endpoint'))
    return server.Server(DjangoidStore(), url)


#Get a DjangoidUser object, based on a delegate URI
def get_djangoid_user_from_identity():
    user = DjangoUser.objects.filter(is_superuser=True)
    if len(user) == 0:
        raise Exception("No superusers exist")
    djangoid, created = DjangoidUser.objects.get_or_create(user=user[0])
    return djangoid


def convertToHttpResponse(response):
    """
    Convert an OpenID server response to a Django-compatible HttpResponse:
    copy HTTP headers, and payload
    """
    r = get_server().encodeResponse(response)
    ret = HttpResponse(r.body)
    for header, value in r.headers.iteritems():
        ret[header] = value
    ret.status_code = r.code
    return ret


@render_to("openidserver/accept_root.html")
def accept(request):
    openid_request = get_server().decodeRequest(dict(request.REQUEST.items()))

    if openid_request is None:
        return HttpResponse("Nothing here")

    if request.method == "GET":
        return {"openid_request": openid_request}

    if request.method == "POST":
        if 'cancel' in request.POST:
            return convertToHttpResponse(openid_request.answer(False))
        if 'remember' in request.POST:
            user = get_djangoid_user_from_identity()
            root = TrustedRoot.objects.get(root = openid_request.trust_root)
            user.trusted_roots.add(root)
        return convertToHttpResponse(openid_request.answer(True))


def endpoint(request):
    openid_request = get_server().decodeRequest(dict(request.REQUEST.items()))
    if openid_request is None:
        return HttpResponse("This was not valid OpenID request")

    if openid_request.mode not in ("checkid_immediate", "checkid_setup"):
        return convertToHttpResponse(get_server().handleRequest(openid_request))

    djangoid = get_djangoid_user_from_identity()
    if not request.user.is_authenticated():
        if openid_request.claimed_id is None:
            openid_request.claimed_id = openid_request.identity
        return redirect_to_login(
            urllib.quote(openid_request.encodeToURL(request.build_absolute_uri())),
            login_url=reverse('login'))
    if request.user != djangoid.user:
        raise Exception("Logged in as %s while expecting %s" % (request.user, djangoid.user))

    # Is the user authenticated, and does he trust this trust_root?
    # user logged in (using openid_request.identity and openid_request.trust_root)
    if djangoid.authenticate(openid_request.trust_root):
        response = openid_request.answer(True)
    elif openid_request.immediate:
        response = openid_request.answer(False, request.META["HTTP_HOST"])
    else:
        if openid_request.claimed_id is None:
            openid_request.claimed_id = openid_request.identity
        redirect = openid_request.encodeToURL(reverse('openid_accept'))
        return HttpResponseRedirect(redirect)
    return convertToHttpResponse(response)

