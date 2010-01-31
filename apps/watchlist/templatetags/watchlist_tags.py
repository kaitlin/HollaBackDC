from django import template
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from watchlist.models import Subscription

register = template.Library()


@register.simple_tag
def unsubscribe_url(obj):
    ctype = ContentType.objects.get_for_model(obj)
    return reverse('watchlist:wl_unsubscribe', args=['.'.join((ctype.app_label, ctype.model)), obj.pk], current_app='watchlist')

@register.simple_tag
def unsubscribe_type_url(content_type):
    return reverse('watchlist:wl_unsubscribe_type',args=['.'.join((content_type.app_label, content_type.model))])

@register.simple_tag
def subscribe_url(obj):
    ctype = ContentType.objects.get_for_model(obj)
    return reverse('watchlist:wl_subscribe', args=['.'.join((ctype.app_label, ctype.model)), obj.pk])

@register.filter
def is_subscribed_to(user, obj):
    if not user.is_authenticated():
        return False
    ctype = ContentType.objects.get_for_model(obj)
    try:
        Subscription.objects.get(user=user, content_type=ctype, object_id=obj.pk)
        return True
    except Subscription.DoesNotExist:
        return False
