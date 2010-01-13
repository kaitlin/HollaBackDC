# -*- mode: python; coding: utf-8; -*-

def as_json(errors):
    return dict((k, map(unicode, v)) for k, v in errors.items())
