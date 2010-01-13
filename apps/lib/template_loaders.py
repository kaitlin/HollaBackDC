# -*- mode: python; coding: utf-8; -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist, loader
from django.utils._os import safe_join

def get_theme_template(template_name, template_dirs=None):
    """
    Template loader, which returns template path accordingly to THEME setting.

    Requires PROJECT_ROOT setting.
    """
    if not (hasattr(settings, 'THEMES_DIR') and hasattr(settings, 'THEME')):
        raise ImproperlyConfigured("There is no THEMES_DIR or THEME setting")
    filepath = safe_join(settings.THEMES_DIR, settings.THEME, template_name)
    try:
        return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
    except IOError:
        raise TemplateDoesNotExist("Tried %s" % filepath)

get_theme_template.is_usable = True


TEMPLATE_CACHE = {}
def cached_get_template(template_name):
    global TEMPLATE_CACHE
    t = TEMPLATE_CACHE.get(template_name, None)
    if not t or settings.DEBUG:
        source, origin = loader.find_template_source(template_name)
        t = loader.get_template_from_string(source, origin, template_name)
        TEMPLATE_CACHE[template_name] = t
    return t
