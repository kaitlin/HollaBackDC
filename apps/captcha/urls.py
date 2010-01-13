# -*- mode: python; coding: utf-8; -*-

from django.conf.urls.defaults import *

import captcha.views

urlpatterns = patterns('',
    url(r'^(?P<captcha_id>\w+)/$', captcha.views.captcha_image, name='captcha_image'),
)

