from django.conf.urls.defaults import *

from haystack.query import SearchQuerySet
from haystack.views import SearchView

sqs = SearchQuerySet().order_by('-date')

urlpatterns = patterns(
    '',
    url(r'^$', SearchView(searchqueryset=sqs), name='post_search'),
)

