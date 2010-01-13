from BeautifulSoup import BeautifulSoup

def _clean_body(text):
    """
    Remove ambigous info (from <user> and tags)
    from SlideShare's item text

    >>> _clean_body('<div class="snap_preview"><img src="http://cdn.slidesharecdn.com/sqlalchemy-seminar-090427104510-phpapp01-thumbnail-2?1240847701" alt ="" style="border:1px solid #C3E6D8;float:right;" /> <p>from: <a href="http://www.slideshare.net/j2a">j2a</a> 2 weeks ago</p><p>Seminar topic about SQLAlchemy -- Pythonic ORM and SQL toolkit.</p><p>Tags: <a style="text-decoration:underline;" href="http://slideshare.net/tag/python">python</a> <a style="text-decoration:underline;" href="http://slideshare.net/tag/sqlalchemy">sqlalchemy</a> </p></div>')
    '<p>Seminar topic about SQLAlchemy -- Pythonic ORM and SQL toolkit.</p>'
    """
    bs = BeautifulSoup(text)
    content = bs.findAll('p')[1:-1]
    return '\n'.join(str(el) for el in content)

def adapt_slides(postfeed):
    postfeed['body'] = _clean_body(postfeed['body'])
    return postfeed

if __name__ == '__main__':
    import doctest
    doctest.testmod()
