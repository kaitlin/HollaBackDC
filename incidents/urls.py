from django.conf.urls.defaults import *

urlpatterns = patterns('incidents.views',
    url(r'^report/$', 'incident_form', name='incident_form'),
)
