from django.contrib.syndication.feeds import Feed as RssFeed
from atom import Feed as AtomFeed

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from lib.helpers import reverse
from life.models import LifeEvent

from feed.blog_feeds import link, get_feed_type

def _LifeEntries(Feed, type='atom'):
    class LifeEntries(Feed):
        def feed_id(self):
            return link(reverse('life_index'))
        link = feed_id

        feed_title = u"%s: Life flow" % Site.objects.get_current().name
        title = feed_title

        def feed_authors(self):
            return ({"name": user.name} for user in User.objects.filter(is_staff=True))

        def feed_links(self):
            return ({'rel': u'alternate', 'href': self.feed_id()},
                    {'rel': u'self', 'href': link(reverse(get_feed_type(type), 'life'))})

        def items(self):
            return LifeEvent.objects.active().order_by('-posted')[:20]

        def item_id(self, item):
            return item.guid

        def item_title(self, item):
            return 'html', item.title

        def item_updated(self, item):
            return item.posted

        item_published = item_updated
        item_pubdate = item_updated

        def item_content(self, item):
            content = u"<p>%s</p><p>// <a href=\"%s\">%s</a></p>" % \
                      (item.body, item.life.link, item.life.name)
            return {'type': 'html'}, content

        def item_links(self, item):
            return ({'rel': u'alternate', 'href': item.link}, )
    return LifeEntries

# Ok, time to build our feeds!
AtomLifeEntries = _LifeEntries(AtomFeed)
RssLifeEntries = _LifeEntries(RssFeed, 'rss')


