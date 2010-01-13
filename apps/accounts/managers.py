# -*- mode: python; coding: utf-8; -*-

import re
import random
from hashlib import sha1

from pytils.translit import slugify
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template import Context, loader
from django.conf import settings

class RegistrationManager(models.Manager):
    """
    Custom manager for the ActionRecord.
    Holds registrations.
    """

    def get_query_set(self):
        """Custom queryset"""
        return super(RegistrationManager, self).get_query_set().filter(type='A')

    def activate_user(self, action_key):
        """
        Given the activation key, makes a User's account active if the
        activation key is valid and has not expired.

        Returns the User if successful, or False if the account was
        not found or the key had expired.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point even trying to look it up
        # in the DB.
        if re.match('[a-f0-9]{40}', action_key):
            try:
                record = self.get(action_key=action_key)
            except self.model.DoesNotExist:
                return False
            if not record.expired:
                # Account exists and has a non-expired key. Activate it.
                user = record.user
                user.is_active = True
                user.save()
                for comment in user.comments.filter(approved=False):
                    comment.approved = True
                    comment.save()
                record.delete()
                return user
        return False

    def create_inactive_user(self, name, email, password, site='', send_email=True):
        """
        Creates a new User and a new ActionRecord for that
        User, generates an activation key, and mails it.

        Pass ``send_email=False`` to disable sending the email.

        You can disable email_sending in settings: DISABLE_REGISTRATION_EMAIL=True

        """
        send_email = not getattr(settings, 'DISABLE_REGISTRATION_EMAIL', False)

        # Create the user.
        new_user = User(username=email.replace('@', '-'), email=email, first_name=name)
        new_user.set_password(password)
        new_user.is_active = False
        new_user.site = site
        new_user.save()

        # Generate a salted SHA1 hash to use as a key.
        salt = sha1(str(random.random())).hexdigest()[:5]
        action_key = sha1(salt+slugify(new_user.email)).hexdigest()

        # And finally create the record.
        new_record = self.create(user=new_user,
                                 action_key=action_key,
                                 type='A')
        if send_email:
            current_domain = Site.objects.get_current().domain
            subject = "Activate your new account at %s" % current_domain
            message_template = loader.get_template('accounts/activation_email.txt')
            message_context = Context({ 'site_url': '%s://%s' % (settings.SITE_PROTOCOL, current_domain),
                                        'action_key': action_key,
                                        'expiration_days': settings.ACTION_RECORD_DAYS,
                                        'password': password,
                                        'user': new_user})
            message = message_template.render(message_context)
            new_user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        return new_user

    def create_user(self, name, email, password, site='', send_email=True, openid=None):
        """
        Create a new User, activate it, send email about password

        You can disable email_sending in settings: DISABLE_REGISTRATION_EMAIL=True
        """
        send_email = send_email and not getattr(settings, 'DISABLE_REGISTRATION_EMAIL', False)

        # Create the user.
        if openid:
            username = openid[7:37]
        else:
            username = email.replace('@', '-')
        try:
            while True:
                User.objects.get(username=username)
                username = username[:-2] + str(random.randrange(10, 100))
        except User.DoesNotExist:
            pass
        new_user = User(username=username, email=email, first_name=name)
        new_user.set_password(password)
        new_user.is_active = True
        new_user.site = site
        new_user.save()

        if send_email:
            current_domain = Site.objects.get_current().domain
            subject = "Your new account at %s has been created" % current_domain
            message_template = loader.get_template('accounts/created_email.txt')
            message_context = Context({'site_url': '%s://%s' % (settings.SITE_PROTOCOL, current_domain),
                                        'password': password,
                                        'user': new_user})
            message = message_template.render(message_context)
            new_user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        return new_user

    def delete_expired_users(self):
        """
        Removes unused records and their associated accounts.

        This is provided largely as a convenience for maintenance
        purposes; if a ActionRecord's key expires without the
        account being activated, then both the ActionRecord and
        the associated User become clutter in the database, and (more
        importantly) it won't be possible for anyone to ever come back
        and claim the username. For best results, set this up to run
        regularly as a cron job.

        It is not so important for this (byteflow) application,
        because only email is important here.

        If you have a User whose account you want to keep in the
        database even though it's inactive (say, to prevent a
        troublemaker from accessing or re-creating his account), just
        delete that User's ActionRecord and this method will
        leave it alone.

        """
        for record in self.all():
            if record.expired:
                user = record.user
                if not user.is_active:
                    user.delete()


class ResetManager(models.Manager):
    """
    Custom manager for ActionRecord.
    Holds password resets.
    """

    def get_query_set(self):
        """Custom queryset"""
        return super(ResetManager, self).get_query_set().filter(type='R')

    def password_reset(self, action_key, send_email=True):
        """
        Given activation key will reset user password and mail it to
        user's email if key is valid and not expired.

        Returns the User if successful, or None if the account was
        not found or the key had expired.

        Pass ``send_email=False`` to disable sending the email.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point even trying to look it up
        # in the DB.
        if not re.match('[a-f0-9]{40}', action_key):
            return None
        try:
            record = self.get(action_key=action_key)
        except self.model.DoesNotExist:
            return None
        if record.expired:
            return None
        # Key valid and not expired. Reset password.
        user = record.user
        import os, binascii
        password = binascii.b2a_base64(os.urandom(6)).strip()
        user.set_password(password)
        user.save()
        if send_email:
            current_domain = Site.objects.get_current().domain
            subject = "Your password at %s resetted" % current_domain
            message_template = loader.get_template('accounts/resetted_email.txt')
            message_context = Context({ 'site_url': '%s://%s' % (settings.SITE_PROTOCOL, current_domain),
                                        'password': password,
                                        'user': user})
            message = message_template.render(message_context)
            user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        record.delete()
        return user

    def create_password_reset(self, user, send_email=True):
        """
        Create ActionRecord for password reset and mails link
        with activation key to user's email.

        Pass ``send_email=False`` to disable sending the email.
        """
        # Generate a salted SHA1 hash to use as a key.
        salt = sha1(str(random.random())).hexdigest()[:5]
        action_key = sha1(salt+user.email).hexdigest()

        # And finally create the record.
        record, created = self.get_or_create(user=user,
                                             type='R',
                                             defaults={'action_key': action_key})

        if send_email:
            current_domain = Site.objects.get_current().domain
            subject = "Reset your password at %s" % current_domain
            message_template = loader.get_template('accounts/reset_email.txt')
            message_context = Context({ 'site_url': '%s://%s' % (settings.SITE_PROTOCOL, current_domain),
                                        'action_key': record.action_key,
                                        'expiration_days': settings.ACTION_RECORD_DAYS,
                                        'user': user})
            message = message_template.render(message_context)
            user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        return record

    def delete_expired_records(self):
        """Removes unused expired password reset records"""
        for record in self.all():
            if record.expired:
                record.delete()

class EmailManager(models.Manager):
    """
    Custom manager for ActionRecord model.
    Holds email changes.
    """
    def get_query_set(self):
        """Custom queryset, returns only ActionRecords for password resets"""
        return super(EmailManager, self).get_query_set().filter(type='E')

    def change_email(self, action_key):
        """
        Given activation key will change user email if key
        is valid and not expired.

        Returns the User if successful, or None if the account was
        not found or the key had expired.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point even trying to look it up
        # in the DB.
        if not re.match('[a-f0-9]{40}', action_key):
            return None
        try:
            record = self.get(action_key=action_key)
        except self.model.DoesNotExist:
            return None
        if record.expired:
            return None
        # Key valid and not expired. Change email.
        user = record.user
        if user.email_new:
            user.email = user.email_new
            user.email_new = ''
        user.save()
        record.delete()
        return user

    def create_email_change(self, user, new_email, send_email=True):
        """
        Create ActionRecord for email change and mails link
        with activation key to user's email.

        Pass ``send_email=False`` to disable sending the email.
        """
        if not user.email:
            user.email = new_email
            user.save()
            return
        # Generate a salted SHA1 hash to use as a key.
        salt = sha1(str(random.random())).hexdigest()[:5]
        action_key = sha1(salt+user.email).hexdigest()

        # And finally create the record.
        user.email_new = new_email
        user.save()
        record, created = self.get_or_create(user=user,
                                             type='E',
                                             defaults={'action_key': action_key})

        if send_email:
            current_domain = Site.objects.get_current().domain
            subject = "Change your email address at %s" % current_domain
            message_template = loader.get_template('accounts/password_reset.txt')
            message_context = Context({'site_url': '%s://%s' % (settings.SITE_PROTOCOL, current_domain),
                                       'action_key': record.action_key,
                                       'expiration_days': settings.ACTION_RECORD_DAYS,
                                       'user': user})
            message = message_template.render(message_context)
            user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        return record

    def delete_expired_records(self):
        """Removes unused expired password reset records"""
        for record in self.all():
            if record.expired:
                record.delete()


class ApprovalManager(models.Manager):
    """Custom manager for ActionRecord. Holds comment approving"""

    def get_query_set(self):
        """Custom queryset, returns only ActionRecords for comment approvals"""
        return super(ApprovalManager, self).get_query_set().filter(type='C')

    def send_approval(self, comment, send_email=True):
        """Sends approval request for non-approved comment."""
        if comment.approved:
            return

        # Generate a salted SHA1 hash to use as a key.
        salt = sha1(str(random.random())).hexdigest()[:5]
        action_key = sha1(salt+comment.user.email.encode('utf-8')).hexdigest()

        record = self.create(user=comment.user, type='C', action_key=action_key)

        if send_email:
            current_domain = Site.objects.get_current().domain
            subject = "Approve your comment at %s" % current_domain
            message_template = loader.get_template('accounts/approve_comment.txt')
            message_context = Context({'site_url': '%s://%s' % (settings.SITE_PROTOCOL, current_domain),
                                        'action_key': record.action_key,
                                        'expiration_days': settings.ACTION_RECORD_DAYS,
                                        'user': comment.user})
            message = message_template.render(message_context)
            comment.user.email_user(subject, message)
        return record

    def approve_comment(self, action_key):
        if re.match('[a-f0-9]{40}', action_key):
            try:
                record = self.get(action_key=action_key)
            except self.model.DoesNotExist:
                return False
            if not record.expired:
                comment = None # fallback if there were no unapproved comments
                for comment in record.user.comments.filter(approved=False):
                    comment.approved = True
                    comment.save()
                record.delete()
                return comment
            else:
                record.delete()
        return False


    def delete_expired_records(self):
        """Removes unused expired comment approve records"""
        for record in self.all():
            if record.expired:
                record.delete()
