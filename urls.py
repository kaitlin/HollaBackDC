from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from django.contrib import admin

admin.autodiscover()

admin.site.root_path= "/admin/"

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += patterns('', 
    url(r'^', include('cms.urls')),
    )

#should go LAST
#urlpatterns += patterns ('', 
#    url(r'^.*', 'hbdc.views.generic', name='programs'),
#    )
