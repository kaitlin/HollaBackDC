from django.conf.urls.defaults import *
from life import views

urlpatterns = patterns('',
    url(r'^fetch/$', views.life_fetch_feeds, name='life_fetch_feeds'),
    url(r'^$', views.life_index, name='life_index'),
)
