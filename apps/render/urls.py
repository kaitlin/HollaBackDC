from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'help/bbcode/$', direct_to_template, {'template': 'render/bbcode_help.html'}),
)

