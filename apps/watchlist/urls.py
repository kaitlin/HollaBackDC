from django.conf.urls.defaults import *

from watchlist import views

urlpatterns = patterns(
    '',
    url(r'^subscribe/(?P<content_type>[\w]+\.[\w]+)/(?P<object_id>\d+)/$', views.subscribe, name="wl_subscribe"),
    url(r'^unsubscribe/(?P<content_type>[\w]+\.[\w]+)/(?P<object_id>\d+)/$', views.unsubscribe, name="wl_unsubscribe"),
    url(r'^unsubscribe-type/(?P<content_type>[\w]+\.[\w]+)/$', views.unsubscribe_type, name="wl_unsubscribe_type"),
    url(r'^list/$', views.list_subscriptions, name="wl_list"),
    )