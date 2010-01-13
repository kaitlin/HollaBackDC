# -*- mode: python; coding: utf-8; -*-

"""
This module provide an orm_debug template tag which allow you to
see all SQL queries of the current request.
"""

import re

from django import template
from django.conf import settings

register = template.Library()

if not settings.DEBUG:
    @register.simple_tag
    def orm_debug():
        return ''
else:
    @register.inclusion_tag('debug/orm_debug.html')
    def orm_debug():
        """
        Django template tag for displaying SQL queries generated with ORM.
        You need jquery framework if you want use EXPLAIN feature.
        """

        try:
            from pygments import highlight
            from pygments.lexers import SqlLexer
            from pygments.formatters import HtmlFormatter
            pygments_installed = True
        except ImportError:
            pygments_installed = False

        from django.db import connection
        queries = connection.queries

        query_time = 0
        query_count = 0

        for count, query in enumerate(queries):
            query['count'] = count
            query_time += float(query['time'])
            query_count += int(1)
            query['sql'] = query['sql'] #.decode('utf-8')

            query['original_sql'] = query['sql']

            # Following actions make SQL qeries more pretty looking
            parts = re.split('.(?:(?=FROM)|(?=WHERE)|(?=INNER)|(?=ON)|(?=ORDER BY))', query['sql'])
            for x in xrange(len(parts)):
                parts[x] = re.sub(r'^FROM ',     'FROM   ', parts[x])
                parts[x] = re.sub(r'^WHERE ',    'WHERE  ', parts[x])
                parts[x] = re.sub(r'^INNER ',    'INNER  ', parts[x])
                parts[x] = re.sub(r'^ON ',       'ON     ', parts[x])
                parts[x] = re.sub(r'^ORDER BY ', 'ORDER  BY ', parts[x])
                parts[x] = re.sub(r'( OR | AND )', r'\n       \1', parts[x])
                parts[x] = re.sub(r',', r',\n        ', parts[x])
            query['sql'] = '\n'.join(parts)

            if pygments_installed:
                formatter = HtmlFormatter()
                query['sql'] = highlight(query['sql'], SqlLexer(), formatter)
                pygments_css = formatter.get_style_defs()
            else:
                pygments_css = ''

        return {'pygments_css': pygments_css,
                'pygments_installed': pygments_installed,
                'query_time': query_time,
                'query_count': query_count,
                'queries': queries}
