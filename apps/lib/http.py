# -*- mode: python; coding: utf-8; -*-

from django.http import HttpResponse
from django.utils import simplejson


class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=simplejson.dumps(data), mimetype='application/json')
