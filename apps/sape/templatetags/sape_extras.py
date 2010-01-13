"""
Examples of usage::

    {% sape_links %}

or::

    {% sape_links 1 %}...{% sape_links 2 %}...{% sape_links %}

or::

    <ul class="foo">{% sape_links_list 2 %}</ul>...
"""
from django import template
from django.conf import settings

from sape import SapeClient, SapeException

register = template.Library()

SAPE_VERBOSE = getattr(settings, 'SAPE_VERBOSE', False)
CLIENT_KEY = 'sape_client_cached'


def build_sape_links_node(parser, token, join):
    parts = token.split_contents()
    if len(parts) > 1:
        number = int(parts[1])
    else:
        number = 0
    return SapeLinksNode(number, join=join)


@register.tag
def sape_links(parser, token):
    return build_sape_links_node(parser, token, join=True)


@register.tag
def sape_links_list(parser, token):
    return build_sape_links_node(parser, token, join=False)


class SapeLinksNode(template.Node):
    def __init__(self, number, join):
        self.number = number
        self.join = join

    def render(self, context):
        if not CLIENT_KEY in context:
            request = context['request']
            try:
                context[CLIENT_KEY] = build_sape_client(request)
            except SapeException, ex:
                return SAPE_VERBOSE and unicode(ex) or ''
        client = context[CLIENT_KEY]

        if not self.join:
            return '\n'.join('<li>%s</li>' % x for x in client.return_links(self.number))
        else:
            return client.return_links(self.number, join=True)


@register.tag
def sape_debug(parser, token):
    return SapeDebugNode()


class SapeDebugNode(template.Node):
    def render(self, context):
        request = context['request']
        try:
            client = build_sape_client(request)
        except SapeException, ex:
            error = unicode(ex)
        else:
            error = ''

        pages_count = 0
        uris_count = 0
        for key, items in client.links.iteritems():
            if not key.startswith('__'):
                pages_count += 1
                uris_count += len(items)

        tpl = 'User: %s, host: %s, error: %s, pages in cache: %s, uris in cache: %s,' +\
              ' cache time: %s, cache updated: %s'
        args = (client.user, client.host, error, pages_count, uris_count,
                client.db_file_mtime, client.db_file_updated)
        return tpl % args


def build_sape_client(request):
    qs = request.META.get('QUERY_STRING', '') or ''
    uri = ''.join([request.path, len(qs) and '?' or '', qs])
    if hasattr(settings, 'SAPE_HOST'):
        host = settings.SAPE_HOST
    else:
        if 'HTTP_HOST' in request.META:
            host = request.META['HTTP_HOST']
        else:
            host = request.META['SERVER_NAME']

    for key in ('SAPE_USER', 'SAPE_DB_FILE'):
        if not hasattr(settings, key):
            raise Exception('settings.%s is undefined' % key)

    client = SapeClient(host=host, user=settings.SAPE_USER,
                        request_uri=uri, db_file=settings.SAPE_DB_FILE)
    return client
