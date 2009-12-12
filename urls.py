from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('myproject',
    url(r'^$', 'hbdc.views.index', name='index'),

    #url(r'^$', 'myproject.sms.views.index', name='index'),
    #url(r'^post/', include('myproject.sms.urls')),
    # Example:
    # (r'^myproject/', include('myproject.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
