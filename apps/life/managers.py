# -*- encoding: utf-8 -*-
from nebula.managers import AggregatedBlogManager, AggregatedPostManager
from life.adapters import adapt

class LifeFlowManager(AggregatedBlogManager):

    def fetch_feeds(self, queryset=None):
        super(LifeFlowManager, self).fetch_feeds(queryset, adapt)

class LifeEventManager(AggregatedPostManager):
    pass

