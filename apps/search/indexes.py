from django.conf import settings

from haystack.indexes import *
from haystack import indexes

class SearchIndex(indexes.SearchIndex):
    def update_object(self, instance, **kwargs):
        qs = self.get_queryset()
        try:
            qs.get(pk=instance.pk)
            self.backend.update(self, [instance])
        except instance.__class__.DoesNotExist:
            self.backend.remove(instance)

class RealTimeSearchIndex(SearchIndex, indexes.RealTimeSearchIndex):
    pass

def search_class():
    if settings.HAYSTACK_SEARCH_AUTOUPDATE:
        return RealTimeSearchIndex
    return SearchIndex
