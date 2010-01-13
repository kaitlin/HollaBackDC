from django.contrib.syndication.feeds import Feed as RssFeed
from atom import Feed as AtomFeed

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from lib.helpers import reverse
from friends.models import FriendPost

from feed.blog_feeds import link, get_feed_type

def _FriendsEntries(Feed, type='atom'):
    class FriendsEntries(Feed):
        def feed_id(self):
            return link(reverse('friends_index'))
        link = feed_id

        feed_title = u"%s: Friends" % Site.objects.get_current().name
        title = feed_title

        def feed_authors(self):
            return ({"name": user.name} for user in User.objects.filter(is_staff=True))

        def feed_links(self):
            return ({'rel': u'alternate', 'href': self.feed_id()},
                    {'rel': u'self', 'href': link(reverse(get_feed_type(type), 'friends'))})

        def items(self):
            return FriendPost.objects.active().order_by('-posted')[:5]

        def item_id(self, item):
            return item.guid

        def item_title(self, item):
            return 'html', u"%s / %s" % (item.title, item.friend.name)

        def item_updated(self, item):
            return item.posted

        item_published = item_updated
        item_pubdate = item_updated

        def item_content(self, item):
            if not item.is_full_entry:
                html = u"%s [...]" % item.spoiler
            else:
                html = item.spoiler
            return {'type': 'html'}, html

        def item_links(self, item):
            return ({'rel': u'alternate', 'href': item.link}, )
    return FriendsEntries

# Ok, time to build our feeds!
AtomFriendsEntries = _FriendsEntries(AtomFeed)
RssFriendsEntries = _FriendsEntries(RssFeed, 'rss')


