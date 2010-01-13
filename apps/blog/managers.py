# -*- mode: python; coding: utf-8; -*-

from datetime import datetime as dt

from django.db import models
from django.contrib.sites.models import Site

from lib import appcheck


SELECT_SQL = {
    'approved_comments_count': 'SELECT COUNT(*) FROM comment_nodes, django_content_type ' \
        'WHERE comment_nodes.content_type_id = django_content_type.id ' \
        'AND django_content_type.model = \'post\' ' \
        'AND comment_nodes.object_id = blog_post.id ' \
        'AND comment_nodes.approved'}
if appcheck.pingback:
    SELECT_SQL.update({
            'pingback_count': (
                'SELECT COUNT(*) FROM pingback, django_content_type '
                'WHERE pingback.content_type_id = django_content_type.id '
                'AND django_content_type.model = \'post\' '
                'AND pingback.object_id = blog_post.id'
                )})
if appcheck.watchlist:
    SELECT_SQL.update({
            'watchlist_count': (
                'SELECT COUNT(*) FROM watchlist_subscription, django_content_type '
                'WHERE watchlist_subscription.content_type_id = django_content_type.id '
                'AND django_content_type.model = \'post\' '
                'AND watchlist_subscription.object_id = blog_post.id'
                )})


class PostManager(models.Manager):
    def get_query_set(self):
        qs = super(PostManager, self).get_query_set()
        qs = qs.extra(select=SELECT_SQL, params=[])
        return qs


class SitePostManager(PostManager):
    def get_query_set(self):
        qs = super(SitePostManager, self).get_query_set()
        qs = qs.filter(site=Site.objects.get_current())
        return qs


class PublicPostManager(SitePostManager):
    def get_query_set(self):
        qs = super(PublicPostManager, self).get_query_set()
        qs = qs.filter(date__lte=dt.now(), is_draft=False)
        return qs
