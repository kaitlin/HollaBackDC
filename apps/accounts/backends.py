# -*- mode: python; coding: utf-8; -*-

from django.contrib.auth.models import User

from accounts.models import ActionRecord

class CommentApprovingBackend(object):
    def authenticate(self, activation_key, action):
        if hasattr(self, '%s_action' % action):
            return getattr(self, '%s_action' % action)(activation_key)
        else:
            return None

    def approve_action(self, activation_key):
        comment = ActionRecord.approvals.approve_comment(activation_key.lower())
        if comment:
            user = comment.user
            user.current_comment = comment
            return user
        else:
            return None

    def activate_action(self, activation_key):
        user = ActionRecord.registrations.activate_user(activation_key.lower())
        if user:
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class EmailBackend(object):
    def authenticate(self, email, password):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
