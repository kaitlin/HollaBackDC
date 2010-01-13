# -*- mode: python; coding: utf-8; -*-

from django.template import Library, Node, TemplateSyntaxError
from django.template.defaulttags import url
from django.contrib.auth.models import User

from lib.helpers import absolutize_uri

register = Library()


def _link(object, anchor=u''):
    if isinstance(object, User):
        link = object.site
        anchor = object.name
    else:
        link = object.get_absolute_url()
        anchor = unicode(object)
    return {
        'url': link,
        'anchor': anchor}


@register.inclusion_tag('lib/link.html')
def link(object, anchor=u''):
    return _link(object, anchor)


@register.inclusion_tag('lib/static_pages.html', takes_context=True)
def static_pages(context, pages):
    return {'pages': pages, 'page_url': context['request'].path }


class AbsoluteURLNode(Node):
    def __init__(self, urlnode):
        self.urlnode = urlnode

    def render(self, context):
        local_url = self.urlnode.render(context)
        if 'request' not in context:
            return local_url
        return absolutize_uri(context['request'], local_url)


@register.tag
def absolute_url(parser, token):
    """This tag has same format, as {% url %}, except it requires
    that context must contain request object (under name 'request')
    """
    urlnode = url(parser, token)
    return AbsoluteURLNode(urlnode)


class AbsolutizeURLNode(Node):
    def __init__(self, local_url):
        self.local_url = local_url

    def render(self, context):
        if 'request' not in context:
            return self.local_url
        return absolutize_uri(context['request'], self.local_url)


@register.tag
def absolutize_url(parser, token):
    """Will make absolute URL from given string.
    Requires request object in context
    """
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError("%s tag requires exactly 1 argument" % bits[0])
    return AbsolutizeURLNode(bits[1])
