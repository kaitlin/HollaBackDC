# -*- mode: python; coding: utf-8; -*-

from urllib2 import urlparse

from pytils.translit import slugify
from django import test
from django.core import mail
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sites.models import Site

from blog.models import Post
from discussion.models import CommentNode
from lib.exceptions import check_redirect
from lib import appcheck


class PostTestCase(test.TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'test')
        self.p1 = Post.objects.create(author=self.user, name="Some name",
                                      site=Site.objects.get_current(),
                                      text="some text, slighty longer than name")

    def testSlug(self):
        self.assertEquals(slugify(self.p1.name), self.p1.slug)

    def testName(self):
        response = self.client.get(self.p1.get_absolute_url())
        self.assertContains(response, self.p1.name)

    def testContent(self):
        response = self.client.get(self.p1.get_absolute_url())
        self.assertContains(response, self.p1.html.encode('utf-8'))

    def testComment(self):
        self.client.login(email='test@test.com', password='test')
        comment_text = 'some various text for testing'
        check_redirect(lambda: self.client.post(self.p1.get_absolute_url(),
                                                {'body': comment_text}))
        self.comments = CommentNode.objects.for_object(self.p1)
        self.assertEquals(len(self.comments), 1)
        self.assertEquals(comment_text, self.comments[0].body)

    def testLoggedOutComment(self):
        comment_text = 'another comment'
        data = {'body': comment_text, 'name': self.user.username,
                'email': self.user.email, 'subscribe': True}
        check_redirect(lambda: self.client.post(self.p1.get_absolute_url(),
                                                data))
        self.comments = CommentNode.all_objects.for_object(self.p1)
        self.assertEquals(len(self.comments), 1)
        self.assertEquals(comment_text, self.comments[0].body)
        self.assertEquals(len(mail.outbox), 1)

    def testAnonymousComment(self):
        comment_text = 'one more comment'
        data = {'body': comment_text, 'name': 'somethingleft',
                'email': 'left@something.com', 'subscribe': True}
        check_redirect(lambda: self.client.post(self.p1.get_absolute_url(),
                                                data))
        self.comments = CommentNode.all_objects.for_object(self.p1)
        self.assertEquals(len(self.comments), 1)
        self.assertEquals(comment_text, self.comments[0].body)
        # Posting second comment
        self.client.logout()
        data = {'body': 'completely useless', 'name': 'somethingright',
                'email': 'right@something.com', 'subscribe': True}
        check_redirect(lambda: self.client.post(self.p1.get_absolute_url(),
                                                data))
        if not appcheck.watchlist:
            # Expect registration mails
            mailcount = 2
        else:
            # Additionally two notification for comment author
            mailcount = 5
        self.assertEquals(len(mail.outbox), mailcount)

    def testDeleteComments(self):
        c = CommentNode(approved=False, body="just test", user=self.user,
                        object=self.p1)
        c.save()
        self.assertEquals(CommentNode.all_objects.count(), 1)
        self.p1.delete()
        self.assertEquals(CommentNode.all_objects.count(), 0)


class RootTestCase(test.TestCase):

    def testIndexRedirect(self):
        if not getattr(settings, 'SET_URL_ROOT_HANDLER', False):
            settings.SET_URL_ROOT_HANDLER = True
        response = self.client.get('/')
        self.assertEquals(response.status_code, 302)
        # Documentation says that we must get response.headers, but
        # instead we have HttpResponseRedirect object here
        self.assertEquals(urlparse.urlsplit(response['Location'])[2],
                          '/' + settings.BLOG_URLCONF_ROOT)
