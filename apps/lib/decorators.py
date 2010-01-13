# -*- mode: python; coding: utf-8; -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

from lib.http import JsonResponse

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response
    function with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use

    Examples::

      @render_to('some/tmpl.html')
      def view(request):
          if smth:
              return {'context': 'dict'}
          else:
              return {'context': 'dict'}, 'other/tmpl.html'

    (c) 2006-2009 Alexander Solovyov, new BSD License
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0],
                                          RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output,
                                          RequestContext(request))
            return output
        wrapper.__name__ = func.__name__
        wrapper.__module__ = func.__module__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return renderer


def ajax_request(func):
    """
    Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JsonResponse with this dict as content.
    """
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            response = func(request, *args, **kwargs)
        else:
            response = {'error': {'type': 405,
                                  'message': 'Accepts only POST request'}}
        if isinstance(response, dict):
            resp = JsonResponse(response)
            if 'error' in response:
                resp.status_code = response['error'].get('type', 500)
            return resp
        return response
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__doc__ = func.__doc__
    return wrapper
