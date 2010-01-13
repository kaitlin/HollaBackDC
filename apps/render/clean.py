# -*- coding: utf-8

def normalize_html(data):
    """
    Apply tidy cleanup for data which should be in unicode
    """

    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(data)
    return unicode(soup)
