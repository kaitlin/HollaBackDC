import re
import urlparse
from django.utils.html import urlize

USER_SUB = (
    re.compile(r'(^|\s)@(.+?)\b'),
    '\\1<a href="http://twitter.com/\\2">@\\2</a>')
KEYWORD_SUB = (
    re.compile(r'(^|\s)#(.+?)\b'),
    '\\1<a href="http://twitter.com/#search?q=%23\\2">#\\2</a>')


def _make_links(tweet):
    """
    Got tweet text and make links to @users and #keywords

    >>> _make_links('@yurevich looks good')
    '<a href="http://twitter.com/yurevich">@yurevich</a> looks good'

    >>> _make_links('example for @yurevich')
    'example for <a href="http://twitter.com/yurevich">@yurevich</a>'

    >>> _make_links('examples for @yurevich and @ingspree.')
    'examples for <a href="http://twitter.com/yurevich">@yurevich</a> and <a href="http://twitter.com/ingspree">@ingspree</a>.'

    >>> _make_links('let\\'s got to #rupyru')
    'let\\'s got to <a href="http://twitter.com/#search?q=%23rupyru">#rupyru</a>'

    >>> _make_links('let\\'s got to #rupyru')
    'let\\'s got to <a href="http://twitter.com/#search?q=%23rupyru">#rupyru</a>'

    >>> _make_links('@ingspree, let\\'s got to #rupyru')
    '<a href="http://twitter.com/ingspree">@ingspree</a>, let\\'s got to <a href="http://twitter.com/#search?q=%23rupyru">#rupyru</a>'

    """
    for pattern, repl in (USER_SUB, KEYWORD_SUB):
        tweet = re.sub(pattern, repl, tweet)
    return tweet

def _clean_name(tweet):
    """
    Remove amibgous user name from feed

    >>> _clean_name('yurevich: jibjib works!')
    u'jibjib works!'
    """
    return tweet.split(u': ', 1)[1]

def _get_tweet_number(tweet_url):
    """
    Return tweet number by it's url

    >>> _get_tweet_number('http://twitter.com/yurevich/statuses/1808292157')
    '#1808292157'

    >>> _get_tweet_number('http://twitter.com/ingspree/status/1808006316')
    '#1808006316'
    """
    path = urlparse.urlparse(tweet_url)[2]
    number = path.split('/')[-1]
    return '#%s' % (number,)

def adapt_tweet(feedpost):
    """
    Adapt Twitter update from feed to appropriate form
    """
    tweet = feedpost['title']
    for action in (_make_links, _clean_name, urlize):
        tweet = action(tweet)
    feedpost['title'] = _get_tweet_number(feedpost['link'])
    feedpost['body'] = u'<p>%s</p>' % tweet
    return feedpost

if __name__ == '__main__':
    import doctest
    doctest.testmod()
