import re
from urllib import urlencode

from openid.consumer.consumer import Consumer, SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from openid.yadis import xri

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list_detail import object_list

from lib.decorators import render_to
from lib.exceptions import RedirectException
from lib.helpers import absolutize_uri

from openidconsumer.util import DjangoOpenIDStore, from_openid_response
from openidconsumer.forms import OpenidSigninForm, OpenidRegistrationForm, OpenidVerifyForm, OpenidAssociateForm
from openidconsumer.models import UserAssociation
from accounts.views import redirect


def get_address(path, request):
    try:
        out = path.split(request.get_host(), 1)[1]
    except AttributeError:
        return None

nickname_re = re.compile(r'^https?://(?:www\.)?([^\.]+)')

next_url_re = re.compile(r'^/[-\w/]+$')
def is_valid_next_url(next):
    # When we allow this:
    #   /openid/?next=/welcome/
    # For security reasons we want to restrict the next= bit to being a local
    # path, not a complete URL.
    return bool(next_url_re.match(str(next)))


@render_to('openid/failure.html')
def default_on_failure(request, message):
    return {'message': message}


def default_on_success(request, identity_url, openid_response):
    if 'openids' not in request.session.keys():
        request.session['openids'] = []

    # Eliminate any duplicates
    request.session['openids'] = [o for o in request.session['openids'] if o.openid != identity_url]
    openid = from_openid_response(openid_response)
    request.session['openids'].append(openid)

    user = authenticate(openid=str(openid))
    if not user:
        return register_new_openid(request)
    login(request, user)

    if is_valid_next_url(request.GET.get('next')):
        next = request.GET['next']
    else:
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')

    return HttpResponseRedirect(next)


@render_to('openid/signin.html')
def signin(request, sreg=None, extension_args={}, on_failure=default_on_failure):
    openid_url = None
    if is_valid_next_url(request.GET.get('next')):
        next = request.GET['next']
    elif is_valid_next_url(get_address(request.META.get('HTTP_REFERER'), request)):
        next = get_address(request.META['HTTP_REFERER'], request)
    else:
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')

    def get_with_next(url, next):
        if next:
            return '%s?%s' % (url, urlencode({'next': next}))
        else:
            return url

    if request.user.is_authenticated() and 'force' not in request.GET:
        return HttpResponseRedirect(next)

    request_path = get_with_next(request.path, next)

    if request.method == 'POST':
        form = OpenidSigninForm(request.POST, auto_id='id_%s')
        if form.is_valid():
            # first remove email and nickname from sreg if the are in to prevent dup
            extension_args['sreg.optional'] = 'email,nickname'
            if sreg:
                sreg = ','.join([arg for arg in sreg.split(',') if arg not in extension_args['sreg.optional']])
                extension_args['sreg.optional'] += ',' + sreg

            trust_root = getattr(settings, 'OPENID_TRUST_ROOT', absolutize_uri(request, '/'))

            redirect_to = get_with_next(absolutize_uri(request, reverse('openid_complete')), next)

            if xri.identifierScheme(form.cleaned_data['openid_url']) == 'XRI' and getattr(
                settings, 'OPENID_DISALLOW_INAMES', False):
                return on_failure(request, _("i-names are not supported"))

            consumer = Consumer(request.session, DjangoOpenIDStore())
            try:
                auth_request = consumer.begin(form.cleaned_data['openid_url'])
            except DiscoveryFailure:
                return on_failure(request, _("The OpenID was invalid"))

            # Add extension args (for things like simple registration)
            for name, value in extension_args.items():
                namespace, key = name.split('.', 1)
                auth_request.addExtensionArg(namespace, key, value)

            redirect_url = auth_request.redirectURL(trust_root, redirect_to)
            return HttpResponseRedirect(redirect_url)
    else:
        form = OpenidSigninForm(auto_id='id_%s')

    return {
        'form': form,
        'action': request_path,
        }


def complete(request, on_success=default_on_success, on_failure=default_on_failure):
    consumer = Consumer(request.session, DjangoOpenIDStore())
    openid_response = consumer.complete(dict(request.GET.items()),
                                        request.GET.get("openid.return_to", "/"))

    if openid_response.status == SUCCESS:
        return on_success(request, openid_response.identity_url, openid_response)
    elif openid_response.status == CANCEL:
        return on_failure(request, _("The request was cancelled"))
    elif openid_response.status == FAILURE:
        return on_failure(request, openid_response.message)
    elif openid_response.status == SETUP_NEEDED:
        return on_failure(request, 'Setup needed')
    else:
        assert False, "Bad openid status: %s" % openid_response.status


def register_new_openid(request):
    if request.GET.get('next'):
        next = "?" + urlencode({
            'next': request.GET['next']
        })
    else:
        next = ''

    openids = request.session.get('openids', [])
    if openids and len(openids) > 0:
        openid = openids[-1] # Last authenticated OpenID
    else:
        raise RedirectException(reverse('openid_signin') + next)

    nickname = openid.sreg.get('nickname', '')
    email = openid.sreg.get('email', '')

    if not nickname:
        nickname = nickname_re.search(openid.openid).group(1)
        if nickname in ('www', 'livejournal', 'users'):
            nickname = ''

    if request.user.is_authenticated():
        form = OpenidAssociateForm(request.user, {'openid': openid.openid})
    else:
        form = OpenidRegistrationForm(openid.openid, {'name': nickname, 'email': email})
    if form.is_valid():
        form.save()
        user = authenticate(openid=openid.openid)
        if user:
            login(request, user)
        next = request.GET.get('next', '').strip()
        if not next or not is_valid_next_url(next):
            next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
        raise RedirectException(next)
    else:
        return register(request)


@render_to('openid/complete.html')
def register(request):
    is_redirect = False
    next=''
    if request.GET.get('next'):
        next = "?" + urlencode({
            'next': request.GET['next']
        })

    openids = request.session.get('openids', [])
    if openids and len(openids) > 0:
        openid = openids[-1] # Last authenticated OpenID
    else:
        return HttpResponseRedirect(reverse('openid_signin') + next)


    nickname = openid.sreg.get('nickname', '')
    email = openid.sreg.get('email', '')

    if not nickname:
        nickname = openid.openid[7:].strip('w.').split('.')[0]
        if nickname in ('www', 'livejournal', 'users'):
            nickname = ''

    form1 = OpenidRegistrationForm(openid.openid, initial={'name': nickname, 'email': email})
    form2 = OpenidVerifyForm(initial={'email': email})

    if request.POST:
        if 'bnewaccount' in request.POST:
            form1 = OpenidRegistrationForm(request.POST)
            if form1.is_valid():
                is_redirect = True
                form1.save()
                user = authenticate(openid=openid.openid)
                if user:
                    login(request, user)
        elif 'bverify' in request.POST:
            form2 = OpenidVerifyForm(request.POST)
            if form2.is_valid():
                is_redirect = True
                user = form2.get_user()
                ua = UserAssociation(openid_url=openid.openid, user=user)
                ua.save()
                login(request, user)

        # redirect, can redirect only if forms are valid.
        if is_redirect:
            next = request.GET.get('next', '').strip()
            if not next or not is_valid_next_url(next):
                next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
                return HttpResponseRedirect(next)

    return {
        'form1': form1,
        'form2': form2,
        'action': reverse('openidconsumer.views.register') + next,
        'nickname': nickname,
        'email': email,
        }


def signout(request):
    request.session['openids'] = []
    next = request.GET.get('next', '/')
    if not is_valid_next_url(next):
        next = '/'

    logout(request)

    return HttpResponseRedirect(next)


@login_required
def openid_list(request, **kwargs):
    kwargs['queryset'] = UserAssociation.objects.filter(user=request.user)
    kwargs['template_name'] = 'openid/list.html'
    kwargs['extra_context'] = {'form': OpenidSigninForm(auto_id='id_%s')}
    return object_list(request, **kwargs)


@login_required
def delete(request):
    next = redirect(request)
    if not request.method == 'POST' or not request.POST.get('openid'):
        raise RedirectException(next, _('Invalid POST data'))
    if not UserAssociation.objects.filter(user=request.user).count() > 1 and not request.user.email:
        raise RedirectException(next, _("You must have at least one OpenID if you don't have email!"))
    try:
        ua = UserAssociation.objects.get(openid_url=request.POST['openid'], user=request.user)
        ua.delete()
    except UserAssociation.DoesNotExist:
        pass
    raise RedirectException(next, _("OpenID deassociated successfully"))
