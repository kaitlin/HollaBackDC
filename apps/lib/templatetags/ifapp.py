# -*- mode: python; coding: utf-8; -*-

from django import template

from lib import appcheck

register = template.Library()


class IfAppNode(template.Node):
    def __init__(self, do_parse, nodelist):
        self.do_parse = do_parse
        if do_parse:
            self.nodelist = nodelist

    def render(self, context):
        if self.do_parse:
            return self.nodelist.render(context)
        return ''


@register.tag
def ifapp(parser, token):
    """
    Checks if application is loaded and then (and only then) evaluates
    contents of the block:

        {% ifapp debug %}
          {% load orm_debug %}
          {% orm_debug %}
        {% endifapp %}

    It doesn't support variables in place of application name.
    """
    try:
        name, app = token.contents.split()
    except ValueError:
        raise template.TemplateSyntaxError("'ifapp' statement requires one argument")
    end_tag = 'end' + name
    do_parse = getattr(appcheck, app)
    if do_parse:
        nodelist = parser.parse([end_tag])
        parser.delete_first_token()
    else:
        nodelist = parser.skip_past(end_tag)
    return IfAppNode(do_parse, nodelist)
