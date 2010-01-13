from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe

from lib.helpers import reverse
from revcanonical.utils import encode

register = template.Library()


@register.simple_tag
def revcanonical(obj):
    url = reverse('revcanonical', encode(obj))
    site = getattr(settings, 'REVCANONICAL_SITE', None)
    if not site:
        site = Site.objects.get_current().domain
    return mark_safe(u'<link rev="canonical" href="http://%s%s" />' % (site, url))


@register.simple_tag
def shorturl(obj):
    return reverse('revcanonical', encode(obj))
