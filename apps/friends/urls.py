from django.conf.urls.defaults import *
from friends import views

urlpatterns = patterns('',
    url(r'^opml/$', views.friends_opml, name='friends_opml'),
    url(r'^fetch/$', views.friends_fetch_feeds, name='friends_fetch_feeds'),
    url(r'^$', views.friends_index, name='friends_index'),
    url('^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.friends_archive_day, name='friends_day_archive'),
    url('^(?P<year>\d{4})/(?P<month>\d{2})/$', views.friends_archive_month, name='friends_month_archive'),
    url('^(?P<year>\d{4})/$', views.friends_archive_year, name='friends_year_archive'),
)
