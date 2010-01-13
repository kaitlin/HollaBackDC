from django.db import models
from django.utils.translation import ugettext_lazy as _

from lib.helpers import get_object_or_none
from blog.models import Post


SCREEN_CHOICES = (
    ('A', _('All')),
    ('R', _('Anonymous only')),
    ('F', _('non-Friends')),
    ('N', _('None')),
)

ACCESS_LEVELS = (
    ('public', 'Public'),
    ('private', 'Private'),
)

class LiveJournalPost(models.Model):
    post = models.ForeignKey(Post, editable=False, db_column='post_id', related_name='livejournalpost')
    lj_id = models.IntegerField(editable=False, blank=True, null=False)

    need_crosspost = models.BooleanField(_('Needs crossposting'), default=True)

    no_comments = models.BooleanField(_('Turn off comments'), default=False)
    screen_comments = models.CharField(_('Comments screening'), max_length=1, choices=SCREEN_CHOICES, blank=False, default='N')
    access_level = models.CharField(_('Access level'), max_length=10, choices=ACCESS_LEVELS, blank=False, default='public')

    def __unicode__(self):
        return u'%s' % self.post


def get_lj_object_link(post):
    lj = get_object_or_none(LiveJournalPost, post=post)
    if lj:
        return '<a href="../../livejournal/livejournalpost/%s/">edit</a>' % lj.pk
    else:
        return ''
get_lj_object_link.allow_tags = True

Post.add_to_class('lj_object', get_lj_object_link)
