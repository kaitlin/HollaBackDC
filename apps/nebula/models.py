import datetime

from pytils.translit import slugify
import feedparser, feedfinder
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from nebula.debugging import *
from tagging.fields import TagField
from nebula.utilities import fetch_single_feed
from nebula.time_utilities import tzlocal, utc
from nebula.managers import AggregatedBlogManager, AggregatedPostManager

class AggregatedBlog(models.Model):
    """A blog or blog-like website run by an individual or corporation"""
    name = models.CharField(_('name'), blank=True, max_length=255,
        help_text=_("Name of the aggregated site"))
    slug = models.SlugField(_('slug'), blank=True,
        help_text=_("Slug, populates automatically from name"))
    link = models.URLField(_('link'), blank=False, verify_exists=False,
        help_text=_("Link to site"))
    feed = models.URLField(_('feed'), verify_exists=False, blank=True,
        help_text=_("Link to feed, discovered automatically if not filled"))
    owner = models.CharField(_('owner'), blank=True, max_length=100)
    active = models.BooleanField(_('active'), default=True,
        help_text=_("Item is active, fetch it and show in list"))

    bad_dates = models.BooleanField(_('bad dates'), default=False)
    bad_tags = models.BooleanField(_('no tags'), default=False)
    etag = models.CharField(_('etag'), blank=True, max_length=50)
    target = models.CharField(_('target app'), blank=True, max_length=50)

    site = models.ForeignKey(Site, related_name='nebula')    # multisite support
    author = models.ForeignKey(User, related_name='nebula')  # multiuser support

    objects = AggregatedBlogManager()

    class Meta:
        verbose_name        = _('blog')
        verbose_name_plural = _('blogs')
        ordering            = ('name',)

    def fetch(self):
        fetch_single_feed(self)

    def save(self, **kwargs):
        if not self.feed or not self.link or not self.name:
            logging.info("Not all required info is available (feed=%r, link=%r, name=%r), finding it" % (self.feed, self.link, self.name))
            feed_location = None
            if self.feed:
                feed_location = self.feed
            elif self.link:
                logging.info('Finding feed at link %s' % self.link)
                feed_location = feedfinder.feed(self.link)
            else:
                logging.error('Neither link nor feed location is not available')

            if not self.feed and feed_location:
                logging.info('Updating blog feed url from feed -- %s' % feed_location)
                self.feed = feed_location

            if (not self.name or not self.link) and feed_location:
                logging.info('Parsing feed to find additinal info from %s' % feed_location)
                try:
                    d = feedparser.parse(feed_location)
                except:
                    logging.error('Could not process feed %s' % feed_location)
                    return
                feed_title = d.feed.title
                feed_link = d.feed.link
                # Update as many blank fields from feed
                if not self.name:
                    logging.info('Updating blog name from feed -- %r' % feed_title)
                    self.name = feed_title
                if not self.link:
                    logging.info('Updating blog url from feed -- %s') % feed_location
                    self.link = feed_link

                owner = d.entries[0].get('author_detail', None)
                if not owner:
                    owner = d.entries[0].get('author', None)
                else:
                    owner = owner.name
                if owner:
                    self.owner = owner

            if self.slug == '':
                self.slug = slugify(self.name)[:50]
        # Call real save function
        super(AggregatedBlog, self).save(**kwargs)

    @permalink
    def get_absolute_url(self):
        return ('nebula_blog_detail', None, { 'slug':self.slug })

    def __unicode__(self):
        return u"%s" % (self.name,)

class AggregatedPost(models.Model):
    """A post or article from a blog"""
    blog    = models.ForeignKey(AggregatedBlog)
    title   = models.CharField(_('title'), blank=True, max_length=255)
    slug    = models.SlugField(_('slug'))
    link    = models.URLField(_('link'), blank=True, verify_exists=False)
    body    = models.TextField(_('body'), blank=True)
    posted  = models.DateTimeField(_('posted'), blank=True, default=datetime.datetime.now)
    guid    = models.CharField(_('guid'), blank=True, max_length=255)
    author  = models.CharField(_('author'), blank=True, max_length=255)
    active  = models.BooleanField(default=True)
    tags    = TagField()

    objects = AggregatedPostManager()

    class Meta:
        verbose_name        = _('post')
        verbose_name_plural = _('posts')
        ordering            = ('-posted',)
        get_latest_by       = 'posted'

    def __unicode__(self):
        return u"%s" % (self.title,)

    def get_absolute_url(self):
        return self.link

    @property
    def posted_tz(self):
        return self.posted.replace(tzinfo=utc).astimezone(tzlocal)

