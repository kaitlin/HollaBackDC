# -*- mode: python; coding: utf-8; -*-

from django.template import Library, loader
from django.utils.safestring import mark_safe

register = Library()

@register.filter
def authorlink(author):
    """
    This filter link to author-based archives.

    For correct work there must be defined url with name:
        - post_by_author
    """
    return mark_safe(loader.render_to_string('templatetags/authorlink.html',
                                             {'author': author}))
