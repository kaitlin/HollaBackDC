import re
import feedparser
import urllib2
import datetime
from BeautifulSoup import BeautifulSoup

from nebula.debugging import logging
from nebula.time_utilities import time_to_datetime
from pytils.translit import slugify

VERSION = '0.1'
URL = 'http://pyobject.ru/about/nebula/'
USER_AGENT = 'nebula %s - %s' % (VERSION, URL)

def shorten_url(url):
    quoted = urllib2.quote(url)
    req = 'http://is.gd/api.php?longurl=%s' % quoted
    res = urllib2.urlopen(req)
    retcode = res.code
    if retcode != 200:
        raise RuntimeError("Cannot shorten url because is.gd returns non-ok status code: %d" % retcode)
    return res.read()


def clean_body(body):
    headings_start = re.compile(r'(<[h|H]\d{1}>)')
    headings_end = re.compile(r'(</?[h|H]\d{1}>)')
    divs = re.compile(r'(<[/]?div.*?>)')
    comments = re.compile(r'(<!--.*?-->)')
    body = divs.sub('', body)
    body = headings_start.sub('<p class="heading">', body)
    body = headings_end.sub('</p>', body)
    body = comments.sub('', body)

    # Remove junky feedburner links:
    # Note, we don't remove all links that reference feedburner,
    #  only those which contain image elements that reference
    #  feedburner.

    # You cannot simply remove all links that point to feedburner
    #  because some publishers use a feature that rewrites all links
    #  in the content to proxy through FB for tracking purposes.
    if 'feedburner' in body:
        soup = BeautifulSoup(body)
        images = soup.findAll('img', src=re.compile('feedburner'))
        for i in images:
            # Remove the parent link (and by association, the image)
            i.parent.extract()
        body = unicode(soup) # Using unicode to be nice, I guess. str()
                             #  might work just as well.
    return body.strip()

def clean_title(title):
    if title:
        bracketed_text = re.compile(r'\[(.*?)\]')
        title = bracketed_text.sub('', title)
        return title.strip()
    else:
        return ''

def fetch_single_feed(blog, callback_filter=None):
    num_with_tags = 0
    from nebula.models import AggregatedBlog, AggregatedPost
    logging.debug('Fetching feed %s from blog %r' % (blog.feed, blog.name))
    assert isinstance(blog, AggregatedBlog)
    FeedPostClass = getattr(blog, '_post_class', AggregatedPost)
    assert issubclass(FeedPostClass, AggregatedPost), "blog._post_class is %s class instead of subclass of AggregatedBlog" % FeedPostClass.__name__

    if not blog.feed:
        logging.info('Blog %r have no feed' % blog.name)
        return
    try:
        d = feedparser.parse(blog.feed, agent=USER_AGENT, etag=blog.etag)
    except Exception, e:
        logging.error("Fail to fetch feed %s from blog %r: %s" % (blog.feed, blog.name, e))
    status = d.get('status')
    if status:
        if status == 304:
            logging.debug('Feed %s has not changed since our last attempt' % blog.feed)
        elif status >= 400:
            logging.error('HTTP error while trying to grab the feed %s: %s' % (blog.feed, status))
            return
    blog.etag = d.get('etag') or ''
    for entry in d.entries:
        created = False
        active = True

        guid = entry.get('guid', entry.get('link'))

        if not guid:
            logging.warning('Entry %r from feed have %s no guid' % (entry.title, blog.feed))
            continue

        try:
            existing_post = FeedPostClass.objects.get(guid__iexact=guid)
            continue
        except FeedPostClass.DoesNotExist:
            logging.debug('Post %r from feed %s does not already exist in DB' % (guid, blog.feed))
            pass

        date_posted = entry.get('modified_parsed', None)
        if date_posted:
            date_posted = time_to_datetime(date_posted)
        else:
            logging.warning('Blog %r has bad dates' % (blog.name,))
            blog.bad_dates = True
            date_posted = datetime.datetime.now()
        title = entry.get('title', None)
        body = entry.get('summary', None)
        if not body:
            body = getattr(entry, 'content', [{}])[0].get('value', '')
        if body != '':
            body = clean_body(body)
        if title == body:
            body = ''
        if title != '':
            title = clean_title(title)
        link = entry.get('feedburner_origlink', entry.get('link', None))
        #title = title.encode('ascii', 'xmlcharrefreplace')
        #if body:
        #    body = body.encode('ascii', 'xmlcharrefreplace')
        #author = None
        author = entry.get('author_detail')
        if not author:
            author = entry.get('author', '')
        else:
            author = author.get('name', '')
        #if author:
        #    author = author.encode('ascii', 'xmlcharrefreplace')
        #else:
        #    author = ''

        # Process tags if they exist
        tags = entry.get('tags', '')
        if tags != '':
            num_with_tags += 1
            tags = ' '.join([tag.term.lower() for tag in tags])
            logging.debug('Found tags for entry %r from feed %s: %s' % (guid, blog.feed, tags,))

        # shorten url if length bigger than 255
        if len(link) >= 255:
            link = shorten_url(link)

        # calls callback filter for entry
        defaults = {
            'blog'  : blog,
            'title' : title,
            'slug'  : slugify(title)[:50],
            'body'  : body,
            'link'  : link,
            'guid'  : guid,
            'author': author,
            'posted': date_posted.replace(tzinfo=None),
            'tags'  : tags,
            'active': not blog.bad_dates,
        }
        post_extra_defaults = getattr(blog, '_post_extra_defaults', {})
        defaults.update(post_extra_defaults)
        if callable(callback_filter):
            # callback filter may return None if this post must be skipped
            appropriate_defaults = callback_filter(defaults)
        else:
            appropriate_defaults = defaults
        if appropriate_defaults:
            post, created = FeedPostClass.objects.get_or_create(
                guid__iexact=guid,
                defaults=appropriate_defaults,
            )
    if num_with_tags == 0:
        logging.debug('Blog %r has no tags' % (blog,))
        blog.bad_tags = True
    else:
        blog.bad_tags = False
    blog.save()

def fetch_feeds(blogs, callback_filter=None):
    for blog in blogs:
        fetch_single_feed(blog, callback_filter)

