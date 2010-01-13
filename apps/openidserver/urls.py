from django.conf.urls.defaults import *

from openidserver import views

urlpatterns = patterns(
    '',
    url(r'^$', views.endpoint, name="openid_endpoint"),
    url(r'accept/$', views.accept, name="openid_accept"),
)
