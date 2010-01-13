# -*- mode: python; coding: utf-8; -*-

from django.conf.urls.defaults import *

from debug import views

urlpatterns = patterns('',
    (r'^explain_query/$', views.explain_query),
)
