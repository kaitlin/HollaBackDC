# -*- mode: python; coding: utf-8; -*-

from django.template import Library, loader
from django.utils.safestring import mark_safe

from lib.helpers import reverse

register = Library()

@register.filter
def datelinks(value, prefix=''):
    """
    This filter formats date as "day.month.year" and sets links to
    day/month/year-based archives.

    For correct work there must be defined urls with names:
        - day_archive
        - month_archive
        - year_archive
    """
    ctx = {'year': reverse(prefix+'year_archive', year=value.year),
           'month': reverse(prefix+'month_archive', year=value.year,
                            month=value.strftime('%m')),
           'day': reverse(prefix+'day_archive', year=value.year,
                          month=value.strftime('%m'),
                          day=value.strftime('%d')),
           'date': value}
    return mark_safe(loader.render_to_string('templatetags/datelinks.html', ctx))


@register.filter
def get_month(date):
    return date.strftime('%m')


@register.filter
def get_day(date):
    return date.strftime('%d')
