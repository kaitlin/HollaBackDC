from django.conf.urls.defaults import *

from revcanonical import views


urlpatterns = patterns(
    '',
    url('^(?P<addr>[0-9A-Za-z]+\.[0-9A-Za-z]+)/$', views.canonical_redirect,
        name="revcanonical"),
)
