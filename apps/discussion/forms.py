# -*- mode: python; coding: utf-8; -*-

import uuid

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from accounts.models import ActionRecord
from discussion.models import CommentNode
from recaptcha.recaptcha_newforms import RecaptchaField
from lib import appcheck


class CommentForm(forms.Form):
    body = CommentNode._meta.get_field('body').formfield()
    subscribe = forms.BooleanField(required=False, initial=True, label=_(u'Subscribe to comments'))
    reply_to = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        kwargs.pop('remote_ip')
        self.user = kwargs.pop('user')
        self.object = kwargs.pop('post')
        super(CommentForm, self).__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated():
            ctype = ContentType.objects.get_for_model(self.object)
            if appcheck.watchlist:
                from watchlist.models import Subscription
                try:
                    Subscription.objects.get(user=self.user, content_type=ctype, object_id=self.object.pk)
                    del self.fields['subscribe']
                except Subscription.DoesNotExist:
                    pass

    def clean_reply_to(self):
        if self.cleaned_data.get('reply_to'):
            try:
                node = CommentNode.objects.get(pk=self.cleaned_data['reply_to'])
            except CommentNode.DoesNotExist:
                raise forms.ValidationError(_(u"You are trying to reply to unavailable comment"))
            if node.object != self.object:
                raise forms.ValidationError(_(u"Trying to reply to comment from another object"))
            self.parent = node
            return self.cleaned_data['reply_to']
        else:
            self.parent = self.object

    def save(self, approved=True, user_is_new=False):
        node = CommentNode(user=self.user, object=self.parent, body=self.cleaned_data['body'], approved=approved)
        node.save()
        if appcheck.watchlist and self.cleaned_data.get('subscribe'):
            from watchlist.models import Subscription
            Subscription.objects.subscribe(self.user, node.object)
        return node, user_is_new


class AnonymousCommentForm(CommentForm):
    name = User._meta.get_field('first_name').formfield(required=True, help_text=_(u'Required. 30 chars of fewer.'), label=_(u'Name'))
    email = User._meta.get_field('email').formfield(required=True, help_text=_(u'Required.'), label=_(u'Email'))
    site = User._meta.get_field('site').formfield()

    def __init__(self, *args, **kwargs):
        if settings.CAPTCHA == 'simple':
            from captcha.fields import CaptchaField
            self.base_fields['captcha'] = CaptchaField()
        elif settings.CAPTCHA == 'recaptcha':
            self.base_fields['captcha'] = RecaptchaField(kwargs['remote_ip'], label=_('Are you human?'))

        super(AnonymousCommentForm, self).__init__(*args, **kwargs)

    def clean_site(self):
        url = self.cleaned_data['site']
        if url:
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'http://%s' % url
            if not forms.fields.url_re.search(url):
                raise forms.ValidationError(u'Please ensure your URL is a full web address (eg: http://google.com/)')
            return url

    def save(self):
        try:
            self.user = User.objects.get(email=self.cleaned_data['email'])
            user_is_new = False
        except User.DoesNotExist:
            func = (settings.ANONYMOUS_COMMENTS_APPROVED
                    and ActionRecord.registrations.create_user
                    or ActionRecord.registrations.create_inactive_user)
            password = uuid.uuid4().hex[:10]
            self.user = func(name=self.cleaned_data['name'],
                             email=self.cleaned_data['email'],
                             password=password,
                             site=self.cleaned_data['site'] or '')
            user_is_new = True

        return super(AnonymousCommentForm, self).save(approved=settings.ANONYMOUS_COMMENTS_APPROVED and user_is_new,
                                                      user_is_new=user_is_new)


