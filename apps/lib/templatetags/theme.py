# -*- mode: python; coding: utf-8; -*-

from time import localtime, strftime
from os.path import join, exists, isdir, getmtime

from django.template import Library
from django.conf import settings

def gettime(filename):
    time = localtime(getmtime(filename))
    return strftime('%Y%m%d%H%M', time)

def theme_static(kind, filename):
    file = '%s.%s' % (filename, kind)
    candidates = [[settings.THEME_STATIC_URL, settings.THEME_STATIC_ROOT, kind, file],
                  [settings.STATIC_URL, settings.STATIC_ROOT, settings.THEME, kind, file],
                  [settings.STATIC_URL, settings.STATIC_ROOT, kind, file]]

    for candidate in candidates:
        full_path = join(*candidate[1:])
        if exists(full_path) and not isdir(full_path):
            url = '/'.join(candidate[2:])
            if settings.APPEND_MTIME_TO_STATIC:
                url = '%s?%s' % (url, gettime(full_path))
            return {'STATIC_URL': candidate[0], 'include': True, 'url': url}

    return {'include': False}

register = Library()

@register.inclusion_tag('templatetags/css.html')
def theme_css(filename='main'):
    return theme_static('css', filename)

@register.inclusion_tag('templatetags/js.html')
def theme_js(filename='main'):
    return theme_static('js', filename)

