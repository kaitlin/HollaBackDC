# -*- mode: python; coding: utf-8; -*-

from django.conf.urls.defaults import *

from accounts import views

urlpatterns = patterns(
    '',
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^auth/$', views.auth, name="auth"),

    url(r'^activate/(?P<activation_key>\w+)$', views.activate, name="account_activate"),
    url(r'^reset/$', views.reset, name="password_reset"),
    url(r'^reset/(?P<activation_key>\w+)$', views.reset, name="password_reset_complete"),
    url(r'^change_email/(?P<activation_key>\w+)$', views.change_email, name="change_email"),
    url(r'^approve_comment/(?P<activation_key>\w+)$', views.approve_comment, name="approve_comment"),

    url(r'^profile/$', views.profile_edit, name="profile_edit"),
    url(r'^merge/$', views.merge, name="merge"),
    )
