from django.db import models
from nebula.models import AggregatedBlog, AggregatedPost
from friends.managers import FriendBlogManager, FriendPostManager
from friends import relations as rels
from django.utils.translation import ugettext_lazy as _

class FriendBlog(AggregatedBlog):
    weight = models.IntegerField(_('Weight'), blank=True, default=0, help_text=_(u'You can order links by this field. Link with smaller number goes first.'))

    rel_friendship = models.CharField(_('Friendship relation'), max_length=20, choices=rels.FRIENDSHIP_REL, blank=True)
    rel_physical = models.CharField(_('Physical relation'), max_length=20, choices=rels.PHYSICAL_REL, blank=True)
    rel_professional =  models.CharField(_('Profesional relation'), max_length=20, choices=rels.PROFESSIONAL_REL, blank=True)
    rel_geographical = models.CharField(_('Geographical relation'), max_length=20, choices=rels.GEOGRAPHICAL_REL, blank=True)
    rel_family = models.CharField(_('Family relation'), max_length=20, choices=rels.FAMILY_REL, blank=True)
    rel_romantic = models.CharField(_('Romantic relation'), max_length=20, choices=rels.ROMANTIC_REL, blank=True)
    rel_identity = models.CharField(_('Identity relation'), max_length=20, choices=rels.IDENTITY_REL, blank=True)

    objects = FriendBlogManager()

    def __unicode__(self):
        return u"Friend: %s" % self.name

    def save(self, **kwargs):
        self.target = self.__class__._meta.app_label
        super(FriendBlog, self).save(**kwargs)

    @property
    def relations(self):
        rels = ['rel_friendship', 'rel_physical', 'rel_professional',
                'rel_geographical', 'rel_family', 'rel_romantic', 'rel_identity']
        return ' '.join(getattr(self, x) for x in rels if getattr(self, x, None))

    @property
    def _post_class(self):
        """
        Post class for this blog
        """
        return FriendPost

    @property
    def _post_extra_defaults(self):
        """
        Post defaults for this blog
        """
        return {'friend': self}

class FriendPost(AggregatedPost):
    friend = models.ForeignKey(FriendBlog)
    spoiler = models.TextField()
    is_full_entry = models.BooleanField()
    objects = FriendPostManager()

    def __unicode__(self):
        return u"Post %s from %s" % (self.title, self.friend)
