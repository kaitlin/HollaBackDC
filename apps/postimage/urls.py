from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^attach/$', 'postimage.views.select', {}, 'postimage_attach'),
    (r'^upload/$', 'postimage.views.upload', {}, 'postimage_upload'),
)
