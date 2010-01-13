# -*- mode: python; coding: utf-8; -*-

import re

from django import template

def tag_parse(contents, param_re):
    """Templatetags parameters parsing helper.

    Require two arguments:

      - ``contents``: ``token.contents``
      - ``param_re``: regexp to parse ``contents`` with.

    Example::

      obj, var = tag_parse(token.contents, r'(\w+) as (\w+)')

    will parse parameters for tag like::

      {% tags_for_object foo_object as tag_list %}
    """
    try:
        tag_name, arg = contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" %
                                           contents.split()[0])
    m = re.search(param_re, arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    return m.groups()
