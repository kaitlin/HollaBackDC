from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from lib.decorators import render_to
from watchlist.models import Subscription


@login_required
@render_to('watchlist/subscribe.html')
def subscribe(request, content_type, object_id):
    app_label, app_model = content_type.split('.')
    ctype = get_object_or_404(ContentType, app_label=app_label, model=app_model)
    obj = get_object_or_404(ctype.model_class(), pk=object_id)
    if request.method == 'POST' and 'Subscribe' in request.POST:
        Subscription.objects.subscribe(request.user, obj)
        return HttpResponseRedirect(request.POST.get('next', obj.get_absolute_url()))
    return {'object': obj, 'next': request.META.get('HTTP_REFERER', obj.get_absolute_url())}


@login_required
@render_to('watchlist/unsubscribe.html')
def unsubscribe(request, content_type, object_id):
    app_label, app_model = content_type.split('.')
    ctype = get_object_or_404(ContentType, app_label=app_label, model=app_model)
    obj = get_object_or_404(ctype.model_class(), pk=object_id)
    if request.method == 'POST' and 'Unsubscribe' in request.POST:
        Subscription.objects.unsubscribe(request.user, obj)
        return HttpResponseRedirect(request.POST.get('next', obj.get_absolute_url()))
    return {'object': obj, 'next': request.META.get('HTTP_REFERER', obj.get_absolute_url())}


@login_required
@render_to('watchlist/unsubscribe.html')
def unsubscribe_type(request, content_type):
    app_label, app_model = content_type.split('.')
    ctype = get_object_or_404(ContentType, app_label=app_label, model=app_model)
    if request.method == 'POST' and 'Unsubscribe' in request.POST:
        Subscription.objects.filter(user=request.user, content_type=ctype).delete()
        return HttpResponseRedirect(request.POST.get('next', '/'))
    return {'ctype': ctype, 'next': request.META.get('HTTP_REFERER', '/')}


@login_required
@render_to('watchlist/list.html')
def list_subscriptions(request):
    return {'object_list': Subscription.objects.filter(user=request.user)}