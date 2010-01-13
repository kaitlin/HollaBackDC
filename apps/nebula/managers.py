from django.db.models import Manager
from nebula.utilities import fetch_feeds

class AggregatedPostManager(Manager):
    def active(self):
        return self.get_query_set().filter(blog__active=True, active=True)

class AggregatedBlogManager(Manager):

    def active(self):
        return self.get_query_set().filter(active=True)

    def fetch_feeds(self, queryset=None, callback_filter=None):
        if not queryset:
            queryset = self.active()
        fetch_feeds(queryset, callback_filter)
