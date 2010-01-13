# -*- mode: python; coding: utf-8; -*-

from django import template
from django.contrib.contenttypes.models import ContentTypeManager

from lib.db import ctm_get
from lib import appcheck

template.add_to_builtins("lib.templatetags.links")
template.add_to_builtins("lib.templatetags.messages")
template.add_to_builtins("blog.templatetags.datelinks")
template.add_to_builtins("typogrify.templatetags.typogrify")
template.add_to_builtins("lib.templatetags.ifapp")
template.add_to_builtins("revcanonical.templatetags.revcanontags")

#if getattr(settings, 'ORM_DEBUG'):
    #template.add_to_builtins("debug.templatetags.orm_debug")

ContentTypeManager.get = ctm_get

from django.forms.util import ErrorDict
if 'as_json' not in ErrorDict.__dict__:
    from lib.ajax import as_json
    ErrorDict.as_json = as_json

if appcheck.watchlist:
    import watchlist.mail

#template.loader.get_template = cached_get_template
