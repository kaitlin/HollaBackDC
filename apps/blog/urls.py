# -*- mode: python; coding: utf-8; -*-

from django.conf.urls.defaults import *
from django.conf import settings

from blog import views

info = {
    'paginate_by': settings.PAGINATE_BY,
    }


urlpatterns = patterns(
    '',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        views.post_detail, name="post_detail"),
    url(r'^(?P<id>[\d]+)/(?P<slug>[-\w]+)/$', views.post_detail_sidebar, name="post-detail-sidebar"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        views.archive_day, name="day_archive"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        views.archive_month, name="month_archive"),
    url(r'^(?P<year>\d{4})/$',
        views.archive_year, name="year_archive"),
    url(r'^tag/(?P<tag>[^/]+)/$', views.by_tag, info, name="post_by_tag"),
    url(r'^$', views.post_list, info, name="post_list"),
    url(r'^comment-edit/(?P<object_id>\d+)/$',
        views.comment_edit, name="comment_edit"),
    url(r'^comment-delete/(?P<object_id>\d+)/$',
        views.comment_delete, name="comment_delete"),
    url(r'^preview/$', views.preview, name="comment_preview"),
    url(r'^processed_js/$', views.processed_js, name="processed_js"),
    url(r'^wysiwyg_js/$', views.wysiwyg_js, name="wysiwyg_js"),
    url(r'^featured/$', views.featured, name="featured_posts"),
    url(r'^tags/$', views.tag_cloud, name="blog_tags"),
    url(r'^author/(?P<author>[\w \.\-\+\|]+)/$',
        views.by_author, info, name="post_by_author"),
    )
