from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(
        regex   = r'^$',
        view    = 'nebula.views.post_list',
        name    = 'nebula_index',
    ),
    url(
        regex   = r'^page/(?P<page>\w)/$',
        view    = 'nebula.views.post_list',
        name    = 'nebula_index_paginated',
    ),
    url(
        regex   = r'^blog/(?P<slug>[-\w]+)/$',
        view    = 'nebula.views.blog_detail',
        name    = 'nebula_blog_detail',
    ),
    url(
        regex   = r'^blog/$',
        view    = 'nebula.views.blog_list',
        name    = 'nebula_blog_list',
    ),
    url(
        regex   = r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        view    = 'nebula.views.post_archive_day',
        name    = 'nebula_post_archive_day',
     ),
     url(
        regex   = r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        view    = 'nebula.views.post_archive_month',
        name    = 'nebula_blog_archive_month',
     ),
     url(
        regex   = r'^(?P<year>\d{4})/$',
        view    = 'nebula.views.post_archive_year',
        name    = 'nebula_blog_archive_year',
     ),
)
