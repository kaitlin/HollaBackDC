from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

from tagging.models import Tag

def list_tags(request):
    try:
        tags = Tag.objects.filter(name__startswith=request.GET['q']).values_list('name', flat=True)
    except MultiValueDictKeyError:
        pass
    return HttpResponse('\n'.join(tags), mimetype='text/plain')
