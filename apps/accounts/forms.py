# -*- mode: python; coding: utf-8; -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserChangeForm
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


from accounts.models import ActionRecord


class BfUserChangeForm(UserChangeForm):
    """
    For prevent error ValidationError when editing user who comes from openid.
    """
    username = forms.CharField(max_length=30, label=_(u'Username'))


class ProfileForm(forms.Form):
    """Form for editing user profile"""
    name = forms.CharField(max_length=30, required=False, label=_(u'Name'))
    email = forms.EmailField(max_length=128, required=False, label=_(u'Email'), help_text=_(u"Changing email requires activation"))
    site = forms.CharField(max_length=200, required=False, label=_(u'Site'))
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False, label=_(u'Password'), help_text=_(u"Leave blank to keep current"))
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False, label=_(u'Password'), help_text=_(u"Repeat, to catch typos"))

    def __init__(self, user, *args, **kwargs):
        """Setting initial values"""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['name'].initial = self.user.first_name
        self.fields['email'].initial = self.user.email
        self.fields['site'].initial = self.user.site

    def clean_name(self):
        try:
            User.objects.exclude(pk=self.user.pk).get(first_name=self.cleaned_data['name'])
            raise forms.ValidationError(_(u'This name is already used by another user. Please choose another.'))
        except User.DoesNotExist:
            return self.cleaned_data['name']

    def clean_email(self):
        """Validates that no user have same email"""
        if self.cleaned_data['email'] and (self.cleaned_data['email'] != self.user.email):
            try:
                User.objects.get(email__iexact=self.cleaned_data['email'])
            except User.DoesNotExist:
                return self.cleaned_data['email']
            raise forms.ValidationError(_(u'This address already belongs to other user'))
        elif not self.cleaned_data['email'] and not self.user.userassociation_set.count():
            raise forms.ValidationError(_(u'This field is required'))
        else:
            return self.cleaned_data['email']

    def clean_password2(self):
        """Validates that the two password inputs match."""
        if self.cleaned_data['password1'] == self.cleaned_data['password2']:
            return self.cleaned_data['password2']
        else:
            raise forms.ValidationError(_(u'You must type the same password each time'))

    def clean_site(self):
        if self.cleaned_data['site'] and self.cleaned_data['site'][:7] != 'http://':
            return 'http://%s' % self.cleaned_data['site']
        else:
            return self.cleaned_data['site']

    def save(self):
        """Saves user profile"""
        self.user.first_name = self.cleaned_data['name']
        self.user.site = self.cleaned_data['site']
        if self.cleaned_data['email'] != self.user.email:
            ActionRecord.emails.create_email_change(self.user, self.cleaned_data['email'])
        # set password only if changed
        if self.cleaned_data.get('password1'):
            self.user.set_password(self.cleaned_data['password1'])
        self.user.save()


class OpenidForm(forms.Form):
    openid_url = forms.URLField(label='OpenID', max_length=200, required=True)

    def __init__(self, session, *args, **kwargs):
        super(OpenidForm, self).__init__(*args, **kwargs)
        self.session = session

    def get_site_url(self):
        from django.contrib.sites.models import Site
        site = Site.objects.get_current()
        return '://'.join(['http', site.domain])

    def clean_openid_url(self):
        #FIXME: lib.auth is not found
        from lib.auth import get_consumer
        from openid.yadis.discover import DiscoveryFailure
        from openid.fetchers import HTTPFetchingError
        consumer = get_consumer(self.session)
        errors = []
        try:
            self.request = consumer.begin(self.cleaned_data['openid_url'])
        except HTTPFetchingError, e:
            errors.append(str(e.why))
        except DiscoveryFailure, e:
            errors.append(str(e[0]))
        if hasattr(self, 'request') and self.request is None:
            errors.append('OpenID service is not found')
        if errors:
            raise forms.ValidationError(errors)

    def auth_redirect(self, target, view_name, *args, **kwargs):
        from django.core.urlresolvers import reverse
        site_url = self.get_site_url()
        trust_url = settings.OPENID_TRUST_URL or (site_url + '/')
        return_to = site_url + reverse(view_name, args=args, kwargs=kwargs)
        self.request.return_to_args['redirect'] = target
        return self.request.redirectURL(trust_url, return_to)

class MergeForm(forms.Form):
    email = forms.EmailField(max_length=128, required=True, label=_(u'Email'), help_text=_(u"Email address of account to merge"))
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label=_(u'Password'))

    def __init__(self, request, *args, **kwargs):
        super(MergeForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("Specified user not found"))
        if not user.check_password(self.cleaned_data['password']):
            raise forms.ValidationError(_("Specified user not found"))
        return {'email':self.cleaned_data['email'], 'password':self.cleaned_data['password']}

    def save(self,):
        """Switch all the foreign keys except Profile"""
        newuser = authenticate(email=self.cleaned_data['email'], password=self.cleaned_data['password'])
        olduser = self.request.user
        from blog.models import Post
        Post.plain_manager.filter(author=olduser).update(author=newuser)
        from discussion.models import CommentNode
        CommentNode.all_objects.filter(user=olduser).update(user=newuser)
        from watchlist.models import Subscription
        Subscription.objects.filter(user=olduser).update(user=newuser)
        from openidconsumer.models import UserAssociation
        UserAssociation.objects.filter(user=olduser).update(user=newuser)

        """Switch the user itself"""
        login(self.request, newuser)
        olduser.delete()
