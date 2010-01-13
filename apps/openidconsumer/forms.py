import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from openid.yadis import xri

from accounts.models import ActionRecord
from openidconsumer.models import UserAssociation


class OpenidSigninForm(forms.Form):
    openid_url = forms.CharField(max_length=255, widget=forms.widgets.TextInput(attrs={'class': 'required openid'}))
    next = forms.CharField(max_length=255,widget=forms.HiddenInput(), required=False)

    def clean_openid_url(self):
        if 'openid_url' in self.cleaned_data:
            openid_url = self.cleaned_data['openid_url']
            if xri.identifierScheme(openid_url) == 'XRI' and getattr(
                settings, 'OPENID_DISALLOW_INAMES', False
                ):
                raise forms.ValidationError(_('i-names are not supported'))
            return self.cleaned_data['openid_url']

    def clean_next(self):
        if 'next' in self.cleaned_data and self.cleaned_data['next'] != "":
            next_url_re = re.compile('^/[-\w/]+$')
            if not next_url_re.match(self.cleaned_data['next']):
                raise forms.ValidationError(_('next url "%s" is invalid' % self.cleaned_data['next']))
            return self.cleaned_data['next']


attrs_dict = { 'class': 'required' }

class OpenidRegistrationForm(forms.Form):
    name = User._meta.get_field('first_name').formfield(required=False)
    email = User._meta.get_field('email').formfield(required=False)

    def __init__(self, openid, *args, **kwargs):
        super(OpenidRegistrationForm, self).__init__(*args, **kwargs)
        self.openid = openid

    def clean_email(self):
        """For security reason one unique email in database"""
        if self.cleaned_data.get('email'):
            try:
                user = User.objects.get(email__exact=self.cleaned_data['email'])
            except User.DoesNotExist:
                return self.cleaned_data['email']
            else:
                raise forms.ValidationError(_(u"This email is already in database. Please choose another."))
        else:
            return ''

    def save(self):
        tmp_pwd = User.objects.make_random_password()
        user = ActionRecord.registrations.create_user(
            self.cleaned_data['name'],
            self.cleaned_data['email'],
            tmp_pwd,
            send_email=False,
            openid=self.openid)

        # make association with openid
        ua = UserAssociation.objects.create(openid_url=self.openid, user=user)
        return user


class OpenidVerifyForm(forms.Form):
    email = User._meta.get_field('email').formfield(required=True)
    password = forms.CharField(max_length=128, widget=forms.widgets.PasswordInput(attrs=attrs_dict))

    def clean_email(self):
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError(_(u"This email doesn't exist. Please choose another."))
        return self.cleaned_data['email']

    def clean_password(self):
        if 'email' in self.cleaned_data and 'password' in self.cleaned_data:
            self.user = authenticate(email=self.cleaned_data['email'], password=self.cleaned_data['password'])
            if self.user is None:
                raise forms.ValidationError(_(u"Please enter a correct email and password. Note that both fields are case-sensitive."))
            elif self.user.is_active == False:
                raise forms.ValidationError(_(u"This account is inactive."))
            return self.cleaned_data['password']

    def get_user(self):
        return self.user


class OpenidAssociateForm(forms.Form):
    openid = UserAssociation._meta.get_field('openid_url').formfield(required=True)

    def __init__(self, user, *args, **kwargs):
        super(OpenidAssociateForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_openid(self):
        try:
            UserAssociation.objects.get(openid_url=self.cleaned_data['openid'])
        except UserAssociation.DoesNotExist:
            return self.cleaned_data['openid']
        else:
            raise forms.ValidationError('OpenID is already associated with some user.')

    def save(self):
        ua = UserAssociation.objects.create(openid_url=self.cleaned_data['openid'], user=self.user)
        return ua
