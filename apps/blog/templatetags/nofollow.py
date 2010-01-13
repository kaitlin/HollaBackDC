# -*- mode: python; coding: utf-8; -*-

from django.template import Library
import re

register = Library()

r_nofollow = re.compile('<a (?![^>]*nofollow)')
s_nofollow = '<a rel="nofollow" '

def nofollow(value):
    """Add a rel="nofollow" attribute to its value.

    Value should be a proper anchor tag.
    """
    return r_nofollow.sub(s_nofollow, value)

register.filter(nofollow)
