# -*- mode: python; coding: utf-8; -*-

from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site

from lib import appcheck
from lib.helpers import reverse, signals
from render import render, RENDER_METHODS
from blog.managers import PostManager, SitePostManager, PublicPostManager
from discussion.models import CommentNode
from tagging_autocomplete.models import TagAutocompleteField
from tagging.utils import parse_tag_input
from tagging.models import Tag
from pingback import Pingback, create_ping_func
from pingback import ping_external_links, ping_directories
import xmlrpc


models.signals.post_save.connect(Site, lambda **kw: Site.objects.clear_cache())
models.signals.post_delete.connect(Site, lambda **kw: Site.objects.clear_cache())


class Post(models.Model):
    site = models.ForeignKey(Site, related_name='posts')
    author = models.ForeignKey(User, related_name='posts')
    name = models.CharField(_(u'Name'), max_length=settings.NAME_LENGTH)
    slug = models.SlugField(_(u'Slug'), max_length=settings.NAME_LENGTH,
                            blank=True, unique_for_date="date")
    text = models.TextField(_(u'Text'),
        help_text=u'Use &lt;!--more--&gt; to separate heading with body')
    render_method = models.CharField(_(u'Render method'), max_length=15,
        choices=RENDER_METHODS, default=settings.RENDER_METHOD)
    html = models.TextField(_(u'HTML'), editable=False, blank=True)
    date = models.DateTimeField(_(u'Date'), default=datetime.now)
    upd_date = models.DateTimeField(_(u'Date'), auto_now=True, editable=False)
    is_draft = models.BooleanField(verbose_name=_(u'Draft'), default=False)
    enable_comments = models.BooleanField(default=True)
    tags = TagAutocompleteField(help_text=u'Delimiters are commas or spaces if there is no commas. Phrases may also be quoted with "double quotes", which may contain commas as part of the tag names they define.')

    comments = generic.GenericRelation(CommentNode)
    pingbacks = generic.GenericRelation(Pingback)

    whole_objects = PostManager()
    all_objects = SitePostManager()
    objects = PublicPostManager()
    plain_manager = models.Manager()

    class Meta:
        db_table = 'blog_post'
        ordering = ['-date']
        get_latest_by = 'date'
        unique_together = ('site', 'slug', 'date')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('post_detail', year=self.date.year,
                       month=self.date.strftime('%m'),
                       day=self.date.strftime('%d'),
                       slug=self.slug)

    def get_absolute_uri(self):
        return '%s://%s%s' % (settings.SITE_PROTOCOL,
                               self.site.domain,
                               self.get_absolute_url())

    def save(self, *args, **kwargs):
        if not self.slug:
            from pytils.translit import slugify
            self.slug = slugify(self.name)
        self.text = self.text.strip()
        self.html = render(self.text, self.render_method, unsafe=True)
        super(Post, self).save(*args, **kwargs)

    def comments_open(self):
        if settings.COMMENTS_EXPIRE_DAYS:
            return self.enable_comments and (datetime.today() - timedelta(settings.COMMENTS_EXPIRE_DAYS)) <= self.date
        else:
            return self.enable_comments
    comments_open.boolean = True

    def get_tags(self):
        return parse_tag_input(self.tags)

    def get_tag_objects(self):
        """Returns real tag objects for given post"""
        return Tag.objects.get_for_object(self)

    @property
    def html_short(self):
        from render.clean import normalize_html
        if self.shortable:
            head = self.html.split('<!--more-->', 1)[0]
            head = normalize_html(head)
            return head
        else:
            return self.html

    @property
    def shortable(self):
        return '<!--more-->' in self.html

    def view_link(self):
        return u'<a href="%s://%s%s">%s</a>' % (
            settings.SITE_PROTOCOL, self.site.domain,
            self.get_absolute_url(), _('view'))
    view_link.allow_tags = True


# Pingback and directory ping handling
def pingback_blog_handler(year, month, day, slug, **kwargs):
    from datetime import time, date, datetime
    from time import strptime
    d = date(*strptime(year + month + day, '%Y%m%d')[:3])
    r = (datetime.combine(d, time.min), datetime.combine(d, time.max))
    return Post.objects.filter(date__range=r).get(slug=slug)

ping_details = {'post_detail': pingback_blog_handler}
xmlrpc.dispatcher.register_function(create_ping_func(**ping_details), 'pingback.ping')


ping_links = ping_external_links(content_attr='html', url_attr='get_absolute_uri',
                                 filtr=lambda x: not x.is_draft)
ping_dirs = ping_directories(content_attr='html', url_attr='get_absolute_uri',
                             filtr=lambda x: not x.is_draft)

if appcheck.pingback:
    signals.post_save(sender=Post)(ping_links)
    signals.post_save(sender=Post)(ping_dirs)


if appcheck.watchlist:
    from watchlist.models import Subscription
    @signals.post_save(sender=Post)
    def subscribe_author(instance, created, **kwargs):
        if not created:
            return
        Subscription.objects.subscribe(instance.author, instance)
