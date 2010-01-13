# -*- mode: python; coding: utf-8; -*-

import urllib

from django.contrib.auth import authenticate, login as log_in, logout as log_out
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from lib.decorators import render_to
from lib.helpers import reverse
from lib.exceptions import RedirectException

from accounts.models import ActionRecord
from accounts.forms import ProfileForm, MergeForm


def redirect(request):
    """Get appropriate url for redirect"""
    next = request.POST.get('next')
    if next:
        return urllib.unquote(next)
    return request.META.get('HTTP_REFERER', '/')


# TODO: make login form, move all logic to it, change message displaying using
# request.session['site_messages']
@render_to("accounts/login.html")
def login(request):
    """Logs in user and redirects to appropriate location"""
    if not request.user.is_anonymous():
        return HttpResponseRedirect(redirect(request))
    response = {}
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        if not (email and password):
            response['error'] = _(u'Email or password was not supplied')
        else:
            user = authenticate(email=email, password=password)
            if user:
                log_in(request, user)
                return HttpResponseRedirect(redirect(request))
            else:
                response['error'] = _(u'Email or password are incorrect!')
    response['next'] = request.REQUEST.get('next', '/')
    return response


def auth(request):
    user = authenticate(session=request.session, query=request.GET)
    if not user:
        return HttpResponseForbidden('Authorization error')
    log_in(request, user)
    return HttpResponseRedirect(request.GET.get('redirect', '/'))


def logout(request):
    log_out(request)
    return HttpResponseRedirect(redirect(request))


@render_to('accounts/activate.html')
def activate(request, activation_key):
    """Activates a user's account, if his key is valid and hasn't expired"""
    user = authenticate(activation_key=activation_key, action='activate')
    if not user:
        return HttpResponseForbidden(_(u'Activation does not exist or already expired.'))
    log_in(request, user)
    return {
        'account': user,
        'expiration_days': settings.ACTION_RECORD_DAYS,
        }


@render_to('accounts/reset.html')
def reset(request, activation_key=None):
    if activation_key:
        user = ActionRecord.resets.password_reset(activation_key.lower())
        return {'success': _(u'Password succesfully resetted. Message with new password was sent to your email.')}
    else:
        if request.method == 'POST':
            if not request.POST['email']:
                return {'error': _(u'Please enter email.')}
            try:
                user = User.objects.filter(is_active=True).get(email__iexact=request.POST['email'])
                ActionRecord.resets.create_password_reset(user)
                return {'success': _(u'Message with instructions to reset password was sent to your email.')}
            except User.DoesNotExist:
                return {'error': _(u'Sorry, no one user is associated with this email.')}
        else:
            return {}


@render_to('accounts/email_changed.html')
def change_email(request, activation_key):
    user = ActionRecord.emails.change_email(activation_key.lower())
    return {'success': _(u'You have succesfully changed your email address!')}


def approve_comment(request, activation_key):
    user = authenticate(activation_key=activation_key, action='approve')
    if not user:
        return HttpResponseForbidden(_(u'Comment approval error'))
    log_in(request, user)
    return HttpResponseRedirect(user.current_comment.get_absolute_url())


@render_to('accounts/profile_detail.html')
def profile_detail(request, slug):
    user = get_object_or_404(User, email=slug)
    return {'object': user}


@login_required
@render_to('accounts/profile_edit.html')
def profile_edit(request):
    from django.utils.translation import ugettext as _
    if request.method == 'POST':
        form = ProfileForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            raise RedirectException(redirect(request), notice_message=_(u'Changes to profile saved.'))
    else:
        form = ProfileForm(request.user)
    return {'form': form}

@login_required
@render_to('accounts/merge.html')
def merge(request):
    """Merges accounts and switches to a new merged account"""
    if request.POST:
        form = MergeForm(request, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("profile_edit"))
        else:
            return {'form':form}
    else:
        form = MergeForm(request)
        return {'form':form}

