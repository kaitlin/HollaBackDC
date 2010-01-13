import urlparse

def _get_user_feed_for(feed_url):
    """
    Return user this activity feed for

    >>> _get_user_feed_for('http://bitbucket.org/j2a/atom/feed/')
    'j2a'
    """
    path = urlparse.urlparse(feed_url)[2]
    return path.split('/')[1]

def adapt_following(postfeed):
    """
    Filter activities for single user
    """
    user = _get_user_feed_for(postfeed['blog'].feed)
    if postfeed['title'] and postfeed['title'].startswith(user):
        return postfeed

if __name__ == '__main__':
    import doctest
    doctest.testmod()
