import urlparse

def _get_micropost_number(micropost_url):
    """
    Return micropost number by it's url

    >>> _get_micropost_number('http://juick.com/j2a/110618')
    '#110618'

    >>> _get_micropost_number('http://juick.com/110618')
    '#110618'
    """
    path = urlparse.urlparse(micropost_url)[2]
    number = path.split('/')[-1]
    return '#%s' % (number,)

def adapt_micropost(feedpost):
    """
    Adapt Juick micropost from feed to appropriate form
    """
    micropost = feedpost['body'] or feedpost['title']
    feedpost['title'] = _get_micropost_number(feedpost['link'])
    feedpost['body'] = micropost
    return feedpost

if __name__ == '__main__':
    import doctest
    doctest.testmod()

