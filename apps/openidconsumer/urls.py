from django.conf.urls.defaults import patterns, url

from openidconsumer import views

urlpatterns = patterns(
    '',
    url(r'^$', views.signin, name="openid_signin"),
    url(r'^list/$', views.openid_list, name="openid_list"),
    url(r'^signout/$', views.signout, name="openid_signout"),
    url(r'^complete/$', views.complete, name="openid_complete"),
    url(r'^register/$', views.register, name="openid_register"),
    url(r'^delete/$', views.delete, name="openid_delete"),
)
