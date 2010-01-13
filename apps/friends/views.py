from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import date_based, list_detail
from lib.helpers import reverse
from friends.models import FriendPost, FriendBlog

try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

def _gen_opml(opmldata, flattened=True):
    """
    Generate OPML document from pythonic dict-like data
    which contains optional head keys (title, dateCreated,
    dateModified, ownerName, ownerEmail, ownerId) and
    required body key with list of dict-like outlines.
    For outline required keys are: type, text, xmlUrl.
    Optional one are: description, htmlUrl, language.

    Example:
        opmldata = {
            ownerId = 'http://pyobject.ru/about/',
            body = [
                dict(text='PyObject', type='pie',
                     xmlUrl='http://feeds.feedburner.com/pyobject',
                     language='ru'),
                dict(text=u'Adam Gomaa', type='rss',
                     xmlUrl='http://adam.gomaa.us/blog/feed/',
                     htmlUrl='http://adam.gomaa.us/',
                     title=u'Adam Gomaa',
                     description='204 No Content Blog'),
            ]
        }

    Set arg flattened to False if you want to get ETree
    istead of xml string.
    """
    opml = ET.Element('opml', version='2.0')
    head = ET.SubElement(opml, 'head')
    for headtag in ('title', 'dateCreated', 'dateModified',
                        'ownerName', 'ownerEmail', 'ownerId'):
        headval = opmldata.get(headtag)
        if headval:
            subel = ET.SubElement(head, headtag)
            subel.text = unicode(headval)
    docs = ET.SubElement(head, 'docs')
    docs.text = "http://www.opml.org/spec2"
    body = ET.SubElement(opml, 'body')
    # we will make plain list of subscriptions, no (sub)folders
    for outval in opmldata['body']:
        outline = ET.SubElement(body, 'outline')
        # required attrs
        for attr in ('type', 'text', 'xmlUrl'):
            outline.set(attr, outval[attr])
        # title is not required, but it's value is the same as text have
        outline.set('title', outval['text'])
        # optional attrs
        for attr in ('description', 'htmlUrl', 'language'):
            val = outval.get(attr)
            if val:
                outline.set(attr, val)
    if flattened:
        return ET.tostring(opml, encoding='utf-8')
    else:
        return opml


def friends_opml(request):
    """
    Generate OPML 2.0 document for friends blogroll
    """
    from django.contrib.auth.models import User
    blogadmin = User.objects.filter(is_superuser=True)[0]
    opmldata = {}
    opmldata['ownerName'] = blogadmin.get_full_name()
    opmldata['ownerEmail'] = blogadmin.email
    opmldata['body'] = []
    for friend in FriendBlog.objects.active():
        outline = {
            'type': 'rss',
            'text': friend.name,
            'xmlUrl': friend.feed,
        }
        if friend.link:
            outline['htmlUrl'] = friend.link
        opmldata['body'].append(outline)
    return HttpResponse(_gen_opml(opmldata), content_type='text/xml')

def friends_index(request):
    """
    Friends index

    Template: ``friends/index.html``
    Context:
      object_list
          list of objects
      is_paginated
          are the results paginated?
      results_per_page
          number of objects per page (if paginated)
      has_next
          is there a next page?
      has_previous
          is there a prev page?
      page
          the current page
      next
          the next page
      previous
          the previous page
      pages
          number of pages, total
      hits
          number of objects, total
      last_on_page
          the result number of the last of object in the
          object_list (1-indexed)
      first_on_page
          the result number of the first object in the
          object_list (1-indexed)
      page_range:
          A list of the page numbers (1-indexed).
    """
    return list_detail.object_list(
        request,
        queryset = FriendPost.objects.active(),
        paginate_by = 10,
        page = request.GET.get('page', 0),
        template_name = 'friends/index.html',
    )

def friends_archive_year(request, year):
    """
    Post archive year

    Templates: ``friends/index.html``
    Context:
    date_list
      List of months in this year with objects
    year
      This year
    object_list
      List of objects published in the given month
      (Only available if make_object_list argument is True)
    """
    return date_based.archive_year(
        request,
        year=year,
        date_field='posted',
        queryset=FriendPost.objects.active(),
        template_name='friends/archive_year.html'
    )

def friends_archive_month(request, year, month):
    """
    Post archive month

    Templates: ``friends/index.html``
    Context:
    month:
      (date) this month
    next_month:
      (date) the first day of the next month,
      or None if the next month is in the future
    previous_month:
      (date) the first day of the previous month
    object_list:
      list of objects published in the given month
    """
    return date_based.archive_month(
        request,
        year=year,
        month=month,
        month_format='%m',
        date_field='posted',
        queryset=FriendPost.objects.active(),
        template_name='friends/index.html'
    )

def friends_archive_day(request, year, month, day):
    """
    Post archive day

    Templates: ``friends/index.html``
    Context:
    object_list:
      list of objects published that day
    day:
      (datetime) the day
    previous_day
      (datetime) the previous day
    next_day
      (datetime) the next day, or None if the current day is today
    """
    return date_based.archive_day(
        request,
        year=year,
        month=month,
        month_format='%m',
        day=day,
        date_field='posted',
        queryset=FriendPost.objects.active(),
        template_name='friends/index.html'
    )

def friends_fetch_feeds(request):
    """
    Manually fetch feeds
    (if don't want to use crontab)
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superuser can fetch friends feeds")
    FriendBlog.objects.fetch_feeds()
    return HttpResponseRedirect(reverse('friends_index'))

