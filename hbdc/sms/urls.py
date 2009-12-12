from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'$', 'myproject.sms.views.post', name='post-page'),
)
