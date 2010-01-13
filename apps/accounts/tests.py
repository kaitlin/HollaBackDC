# -*- mode: python; coding: utf-8; -*-

from django import test
from django.core import mail
from django.contrib.auth.models import User

from accounts.models import ActionRecord
from lib.helpers import reverse
from lib.exceptions import check_redirect


class RegistrationTestCase(test.TestCase):

    def setUp(self):
        self.name = 'megatest'
        self.email = 'something@example.com'
        self.user = ActionRecord.registrations.create_inactive_user(name=self.name, email=self.email, password=self.name)
        self.em = mail.outbox[0]
        self.ar = self.user.actionrecord_set.get(type='A')

    def testUserCreate(self):
        self.assertEquals(self.user.is_active, False)

    def testMailExist(self):
        self.assertEqual(len(mail.outbox), 1)

    def testSubjectValid(self):
        self.assertEqual(self.em.subject, 'Activate your new account at example.com')

    def testContentValid(self):
        self.assertNotEqual(self.em.body.find(self.ar.action_key), -1)

    def testActivation(self):
        user_act = ActionRecord.registrations.activate_user(self.ar.action_key)
        self.assertEqual(self.user, user_act)


class EmailChangeTestCase(test.TestCase):

    def setUp(self):
        self.name = 'test'
        self.old_email = 'something@example.com'
        self.new_email = 'other@example.com'
        self.user = User.objects.create_user(self.name, self.old_email, self.name)

    def testEmailChange(self):
        self.assertEquals(self.client.login(email=self.old_email, password=self.name), True)
        check_redirect(lambda: self.client.post(reverse('profile_edit'),
                                                {'email': self.new_email}))
        self.assertEqual(len(mail.outbox), 1)
