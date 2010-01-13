# -*- mode: python; coding: utf-8; -*-
"""
Add ./manage.py edit id|/url to edit posts in an external editor.

A url may match multiple posts (eg /2009) in which case the editor will be
invoked with many files to edit.  Only modified files will cause database
updates.

by Ben Jackson <ben@ben.com>
"""

import os
from tempfile import mkstemp

import django
from django.core.management.base import LabelCommand, CommandError

from blog.models import Post
from blog.urls import urlpatterns

class Command(LabelCommand):
    help = u'Edit a blog post with an external editor'
    args = u'id|/url...'

    date_fields = ['year', 'month', 'day']

    def match_url(self, url):
        for pat in urlpatterns:
            match = pat.resolve(url) or pat.resolve(url + '/')
            if match:
                func, args, kw = match
                query = dict()
                for field in self.date_fields:
                    if field in kw:
                        query['date__' + field] = int(kw[field])
                        del kw[field]
                query.update(kw)
                return query
        raise CommandError('Cannot match blog url %s' % label)

    def editor(self):
        return getattr(os.environ, 'VISUAL',
               getattr(os.environ, 'EDITOR', 'vi'))

    def update_post(self, post, filename):
        file = open(filename, 'r')
        if not file:
            print "cannot find temp file %s for post %s\n" % (filename, post.get_absolute_url())
            return False
        lines = file.readlines()
        file.close()
        # make EOL match whatever is in the database (probably \r\n)
        if '\r' in post.text:
            lines = [l.rstrip('\n') + '\r\n' for l in lines]
        text = ''.join(lines)
        # avoid updating just because the editor fixed a missing final newline
        if post.text.rstrip('\r\n') != text.rstrip('\r\n'):
            post.text = text
            post.save()
            print 'post %s updated' % post.get_absolute_url();
        else:
            print 'post %s unchanged' % post.get_absolute_url();
        return True

    def edit(self, posts):
        edits = []
        names = []
        for post in posts:
            (fd, name) = mkstemp()
            file = os.fdopen(fd, 'w')
            # this should convert to native EOL
            file.writelines([l + '\n' for l in post.text.splitlines()])
            file.close()
            edits.append((post, name))
            names.append(name)

        if os.system('%s %s' % (self.editor(), ' '.join(names))):
            raise CommandError('Editor %s failed, ignoring changes in files %s' % (self.editor(), ' '.join(names)))

        for post, name in edits:
            self.update_post(post, name)
            os.unlink(name)

    def handle_label(self, label, **opts):
        objects = Post.plain_manager
        if label.startswith('/'):
            query = self.match_url(label.lstrip('/'))
        else:
            try:
                query = {'id': int(label)}
            except ValueError:
                raise CommandError('Expected numeric blog post id or /url, got %s' % label)
        posts = objects.filter(**query)
        if not posts.count():
            raise CommandError('Cannot find blog post %s using query %s' % (label, repr(query)))
        self.edit(posts)
