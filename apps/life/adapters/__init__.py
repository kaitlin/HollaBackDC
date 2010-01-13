# -*- encoding: utf-8 -*-
import urlparse
from life.adapters import twitter, juick, yaru, bitbucket, slideshare

def adapt_nothing(feeditem):
    """
    Do nothing: return item data as is
    """
    return feeditem

def adapt(feeditem):
    source = feeditem['blog'].source
    if source not in ADAPTERS:
        source = 'generic'
    adapter = ADAPTERS[source][2]
    return adapter(feeditem)

def identify_flow(flow_link):
    """
    Identify given flow by it's link

    Always return one of ADAPTERS
    """
    found = None
    host = urlparse.urlsplit(flow_link)[1]
    for source, (description, _uri_key, adapter) in ADAPTERS.items():
        if _uri_key:
            if isinstance(_uri_key, basestring):
                uri_keys = [_uri_key]
            else:
                uri_keys = _uri_key
            for uri_key in uri_keys:
                if host.endswith(uri_key):
                    found = source
    if found is None:
        found = 'generic'
    return found

ADAPTERS = {
    'twitter': ('Twitter updates', 'twitter.com', twitter.adapt_tweet),
    'juick': ('Juick microposts', 'juick.com', juick.adapt_micropost),
    'ya.ru': ('Ya.ru blog feed', 'ya.ru', yaru.adapt_ya_text),
    'delicious': ('Delicious bookmarks', ('delicious.com', 'del.icio.us'), adapt_nothing),
    'bitbucket': ('Bitbucket activities', 'bitbucket.org', bitbucket.adapt_following),
    'github': ('GitHub activities', 'github.com', adapt_nothing),
    'slideshare': ('SlideShare slides', 'slideshare.net', slideshare.adapt_slides),
    'generic': ('Generic blog feed', None, adapt_nothing)
}

SOURCE_CHOICES = tuple((k, v[0]) for k,v in ADAPTERS.items())

