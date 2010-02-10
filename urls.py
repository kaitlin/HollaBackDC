from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from django.contrib import admin
from blog.sitemaps import BlogSitemap, IndexSitemap, BlogTagsSitemap
import patches
from lib import appcheck
from django.contrib.sitemaps import FlatPageSitemap

admin.autodiscover()

admin.site.root_path= "/admin/"

sitemaps = {
    'blog': BlogSitemap,
    'blogtags': BlogTagsSitemap,
    'flat': FlatPageSitemap,
    'index': IndexSitemap,
    }
urlpatterns = patterns('',
    url(r'^admin/postimage/', include('postimage.urls')),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^openid/', include('openidconsumer.urls')),
    url(r'^openidserver/', include('openidserver.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps}),
    url(r'^xmlrpc/', include('xmlrpc.urls')),
    url(r'^robots.txt$', include('robots.urls')),
    url(r'^feeds/', include('feed.urls')),
    url(r'^tagging_autocomplete/', include('tagging_autocomplete.urls')),
)


if appcheck.watchlist:
        urlpatterns += patterns('', url(r'^watchlist/', include('watchlist.urls')),)


if appcheck.wpimport:
    urlpatterns += patterns('', url(r'^wpimport/', include('wpimport.urls')),)

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
