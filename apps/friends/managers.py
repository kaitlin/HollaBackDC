# -*- encoding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from nebula.managers import AggregatedBlogManager, AggregatedPostManager

def shorten_body_filter(postdata, abstract_limit=3, symbols_limit=1500):
    """
    Make shorten body (aka spoiler)
    """
    soup = BeautifulSoup(postdata['body'])
    ps = soup.findAll('p')
    postdata['is_full_entry'] = True
    if len(ps) > abstract_limit+1:
        postdata['spoiler'] = '\n'.join(unicode(p) for p in ps[:abstract_limit])
        postdata['is_full_entry'] = False
    else:
        postdata['spoiler'] = postdata['body']
    if postdata['is_full_entry'] and len(postdata['spoiler']) > symbols_limit:
        # seems that author do not use paragraphs
        # just cut after symbols_limit till las dot
        postdata['spoiler'] = '.'.join(postdata['body'][:symbols_limit].split('.')[:-1])
        postdata['is_full_entry'] = False

    # feed already with spoliers ;)
    if postdata['is_full_entry'] and \
       ( postdata['spoiler'].endswith(u'[...]') or
         postdata['spoiler'].endswith(u'[…]')):
        postdata['is_full_entry'] = False
    return postdata


class FriendBlogManager(AggregatedBlogManager):

    def fetch_feeds(self, queryset=None):
        super(FriendBlogManager, self).fetch_feeds(queryset, shorten_body_filter)

class FriendPostManager(AggregatedPostManager):
    pass

