# -*- mode: python; coding: utf-8; -*-

from datetime import datetime as dt

from django.contrib.syndication.feeds import Feed as RssFeed
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.conf import settings
from django.http import Http404
from django.template.defaultfilters import pluralize

from atom import Feed as AtomFeed

from blog.models import Post
from discussion.models import CommentNode
from lib.helpers import reverse
from lib.db import load_content_objects
from tagging.models import TaggedItem
from tagging.utils import get_tag_list


def link(location):
    return '%s://%s%s' % (settings.SITE_PROTOCOL, Site.objects.get_current().domain, location)


def get_feed_type(feed_type):
    if ((settings.USE_ATOM and feed_type == 'atom') or
        (not settings.USE_ATOM and feed_type == 'rss')):
        return 'feed'
    return '%s_feed' % feed_type


def _BlogEntries(Feed, type='atom'):
    class BlogEntries(Feed):
        def feed_id(self):
            return link(reverse('post_list'))
        link = feed_id

        def feed_title(self):
            return Site.objects.get_current().name
        title = feed_title

        def feed_authors(self):
            return ({"name": user.name} for user in User.objects.filter(is_staff=True))

        def feed_links(self):
            return ({'rel': u'alternate', 'href': self.feed_id()},
                    {'rel': u'self', 'href': link(reverse(get_feed_type(type), 'blog'))})

        def items(self):
            return Post.objects.order_by('-date')[:5]

        def item_id(self, item):
            return link(item.get_absolute_url())

        def item_title(self, item):
            return 'html', item.name

        def item_updated(self, item):
            return item.upd_date

        def item_published(self, item):
            return item.date
        item_pubdate = item_published

        def item_content(self, item):
            html = settings.SHORT_POSTS_IN_FEED and item.html_short or item.html
            return {'type': 'html'}, html

        def item_categories(self, item):
            if (type == 'atom'):
                return ({'term': unicode(tag)} for tag in item.get_tags())
            else:
                return (unicode(tag) for tag in item.get_tags())

        def item_links(self, item):
            return ({'rel': u'self', 'href': self.item_id(item)},
                    {'rel': u'alternate', 'href': self.item_id(item)})
    return BlogEntries

def _PostsByAuthor(Feed, type='atom'):
    class PostsByAuthor(Feed):
        def get_object(self, bits):
            if len(bits) != 1:
                raise Http404
            else:
                try:
                    return User.objects.get(username__exact=bits[0])
                except User.DoesNotExist:
                    raise Http404

        def feed_id(self, author):
            return link(reverse('post_by_author', author=author.username))
        link = feed_id

        def feed_title(self, author):
            site = Site.objects.get_current()
            return u"%s blog posts by author %s" % (site.name, author.name)
        title = feed_title

        def feed_authors(self):
            return ({"name": user.name} for user in User.objects.filter(is_staff=True))

        def feed_links(self, author):
            return ({'rel': u'alternate', 'href': self.feed_id(author)},
                    {'rel': u'self', 'href': link(reverse(
                            get_feed_type(type),
                            'author/%s' % author.username))})

        def items(self, author):
            return Post.objects.filter(author=author).order_by('-date')[:5]

        def item_id(self, item):
            return link(item.get_absolute_url())

        def item_title(self, item):
            return 'html', item.name

        def item_updated(self, item):
            return item.upd_date

        def item_published(self, item):
            return item.date
        item_pubdate = item_published

        def item_content(self, item):
            html = settings.SHORT_POSTS_IN_FEED and item.html_short or item.html
            return {'type': 'html'}, html

        def item_links(self, item):
            return ({'rel': u'self', 'href': self.item_id(item)},
                    {'rel': u'alternate', 'href': self.item_id(item)})

    return PostsByAuthor

def get_tags_bit(tags, union):
    join_string = union and '+' or '|'
    return join_string.join([tag.name for tag in tags])


def list_and_is_union(tagstring):
    if '+' in tagstring:
        return get_tag_list(tagstring.split('+')), True
    else:
        return get_tag_list(tagstring.split('|')), False


def get_posts_from_tags(tags, union):
    if union:
        qs_func = TaggedItem.objects.get_union_by_model
    else:
        qs_func = TaggedItem.objects.get_intersection_by_model
    return qs_func(Post.objects.all(), tags)[:5]


def _PostsByTag(Feed, type='atom'):
    class PostsByTag(Feed):
        def get_object(self, bits):
            if len(bits) != 1:
                raise Http404
            else:
                return list_and_is_union(bits[0])

        def feed_id(self, bits):
            try:
                tags, union = bits
            except TypeError:
                raise Http404
            if not tags:
                raise Http404
            return link(reverse('post_by_tag', tag=get_tags_bit(tags, union)))
        link = feed_id

        def feed_title(self, (tags, union)):
            site = Site.objects.get_current()
            if tags:
                filter_type = union and ' union' or ' intersection'
            else:
                filter_type = ''
            return u"%s blog posts with tag%s%s %s" % (
                site.name,
                pluralize(len(tags)),
                filter_type,
                ', '.join([tag.name for tag in tags]))
        title = feed_title

        def feed_authors(self):
            return ({"name": user.name} for user in User.objects.filter(is_staff=True))

        def feed_links(self, (tags, union)):
            return ({'rel': u'alternate', 'href': self.feed_id((tags, union))},
                    {'rel': u'self', 'href': link(reverse(
                            get_feed_type(type),
                            'tag/%s' % get_tags_bit(tags, union)))})

        def items(self, (tags, union)):
            return get_posts_from_tags(tags, union)

        def item_id(self, item):
            return link(item.get_absolute_url())

        def item_title(self, item):
            return 'html', item.name

        def item_updated(self, item):
            return item.upd_date

        def item_published(self, item):
            return item.date
        item_pubdate = item_published

        def item_content(self, item):
            html = settings.SHORT_POSTS_IN_FEED and item.html_short or item.html
            return {'type': 'html'}, html

        def item_links(self, item):
            return ({'rel': u'self', 'href': self.item_id(item)},
                    {'rel': u'alternate', 'href': self.item_id(item)})
    return PostsByTag


def _CommentEntries(Feed, type='atom'):
    class CommentEntries(Feed):
        # If feed get extra_params, then this will be comments for particular entry,
        # else - all comments
        def get_object(self, bits):
            if len(bits) > 1:
                raise Http404
            elif len(bits) == 1:
                if not bits[0].isnumeric():
                    raise Http404
                try:
                    return Post.objects.get(id=bits[0])
                except Post.DoesNotExist:
                    raise Http404
            else:
                return None

        def feed_id(self, obj):
            if obj:
                return link(obj.get_absolute_url())
            else:
                return link('%s#comments' % reverse('post_list'))
        link = feed_id

        def feed_title(self, obj):
            site = Site.objects.get_current()
            if obj:
                return '%s comments on %s' % (site.name, obj.name)
            else:
                return '%s comments' % site.name
        title = feed_title

        def feed_authors(self, obj):
            if obj:
                return ({'name': c.user.name} for c in obj.comments.all())
            else:
                return ({'name': c.user.name} for c in self.items(obj))

        def feed_links(self, obj):
            return ({'rel': u'alternate', 'href': self.feed_id(obj)},
                    {'rel': u'self', 'href': link(reverse(
                            get_feed_type(type),
                            'comments/%s' % str(getattr(obj, 'id', ''))))})

        def items(self, obj):
            qs = CommentNode.objects
            if obj:
                qs = qs.for_object(obj)
            else:
                # TODO: Beware, that's really hardcoded blog.Post!
                qs = qs.filter(post__site=Site.objects.get_current())
            qs = qs.order_by('-pub_date').select_related(depth=1)[:30]
            load_content_objects(qs, 'object')
            return qs

        def item_id(self, item):
            return link(item.get_absolute_url())

        def item_title(self, item):
            return 'Comment on %s by %s' % (item.object.name, item.user.name)

        def item_updated(self, item):
            return item.upd_date

        def item_published(self, item):
            return item.pub_date
        item_pubdate = item_published

        def item_content(self, item):
            return {'type': 'html'}, item.body_html

        def item_links(self, item):
            return ({'rel': u'self', 'href': self.item_id(item)},
                    {'rel': u'alternate', 'href': self.item_id(item)})

        def item_authors(self, item):
            return ({'name': item.user.name}, )

        def item_in_reply_to(self, item):
            if item.reply_to_id:
                # Nice hack, which will not introduce a lot of queries,
                # because we don't need real object here
                parent = item
                parent.id = item.reply_to_id
                url = self.feed_id(parent)
                return ({'type': u'application/atom+xml',
                         'ref': url,
                         'href': url})

    return CommentEntries


# Ok, time to build our feeds!
AtomBlogEntries = _BlogEntries(AtomFeed)
RssBlogEntries = _BlogEntries(RssFeed, 'rss')
AtomPostsByTag = _PostsByTag(AtomFeed)
RssPostsByTag = _PostsByTag(RssFeed, 'rss')
AtomCommentEntries = _CommentEntries(AtomFeed)
RssCommentEntries = _CommentEntries(RssFeed, 'rss')
AtomPostsByAuthor = _PostsByAuthor(AtomFeed)
RssPostsByAuthor = _PostsByAuthor(RssFeed, 'rss')

# Featured posts feeds
# DRY violation, needs refactoring
class AtomFeaturedBlogEntries(AtomBlogEntries):
    def feed_updated(self):
        return Post.featured_objects.order_by('-date')[0].date

    def items(self):
        return Post.featured_objects.order_by('-date')[:5]

class RssFeaturedBlogEntries(RssBlogEntries):
    def feed_updated(self):
        return Post.featured_objects.order_by('-date')[0].date

    def items(self):
        return Post.featured_objects.order_by('-date')[:5]
