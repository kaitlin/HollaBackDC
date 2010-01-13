from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import list_detail
from lib.helpers import reverse
from life.models import LifeFlow, LifeEvent

def life_index(request):
    """
    Life index

    Template: ``life/index.html``
    """
    return list_detail.object_list(
        request,
        queryset = LifeEvent.objects.active(),
        paginate_by = 20,
        page = request.GET.get('page', 0),
        template_name = 'life/index.html',
    )

def life_fetch_feeds(request):
    """
    Manually fetch feeds
    (if don't want to use crontab)
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superuser can fetch life feeds")
    LifeFlow.objects.fetch_feeds()
    return HttpResponseRedirect(reverse('life_index'))

