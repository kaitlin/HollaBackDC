from django.conf.urls.defaults import *
from django.conf import settings

from wpimport import views

info = {
    'paginate_by': settings.PAGINATE_BY,
    }

# temp
info['paginate_by'] = 30

urlpatterns = patterns(
    '',
    url(r'^$', views.post_list, info),
    url(r'^(\d+)/$', views.post_detail),
    )
