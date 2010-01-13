from django.db import models
from nebula.models import AggregatedBlog, AggregatedPost
from life.managers import LifeFlowManager, LifeEventManager
from life.adapters import SOURCE_CHOICES, identify_flow
from django.utils.translation import ugettext_lazy as _

class LifeFlow(AggregatedBlog):

    objects = LifeFlowManager()

    source = models.CharField(_('source'), max_length=50, choices=SOURCE_CHOICES)

    def __unicode__(self):
        return u"Life flow: %s" % self.name

    def save(self, **kwargs):
        self.target = self.__class__._meta.app_label
        self.source = identify_flow(self.link)
        super(LifeFlow, self).save(**kwargs)

    @property
    def _post_class(self):
        """
        Post class for this blog
        """
        return LifeEvent

    @property
    def _post_extra_defaults(self):
        """
        Post defaults for this blog
        """
        return {'life': self}

class LifeEvent(AggregatedPost):
    life = models.ForeignKey(LifeFlow)
    objects = LifeEventManager()

    def __unicode__(self):
        return u"Item %s from %s" % (self.title, self.life)

