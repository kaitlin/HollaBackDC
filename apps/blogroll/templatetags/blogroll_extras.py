# -*- mode: python; coding: utf-8; -*-

from django import template
from django.db import connection

from blogroll.models import Link

qn = connection.ops.quote_name
register = template.Library()

@register.inclusion_tag('blogroll/links.html')
def blogroll_links():
    """
    Include blogroll: list of links controlled from admin interface, including
    XFN information.

    Renders 'blogroll/links.html' template at the point of inclusion.
    """
    query = """
    SELECT %(link)s.id FROM %(link)s
    ORDER BY %(link)s.weight""" % {
        'link': qn(Link._meta.db_table),
    }
    cursor = connection.cursor()
    cursor.execute(query)
    links = []
    for row in cursor.fetchall():
        links.append(Link.objects.get(id=row[0]))
    return {'links': links
            }
