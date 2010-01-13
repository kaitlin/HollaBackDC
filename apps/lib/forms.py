# -*- mode: python; coding: utf-8; -*-

from lib.exceptions import AjaxDataException


def build_form(Form, _request, *args, **kwargs):
    """Build form using given form class
    Features:
    - detect POST and GET queries
    - detect AJAX queries
    - use initial only in GET queries
    - use POST/FILES only in POST queries

    Arguments:
    - `Form`: form class
    - `_request`: request instance (underscore allow us to give `request` in kwargs)
    """
    if _request.method == 'POST':
        kwargs.pop('initial')
        form = Form(_request.POST, _request.FILES, *args, **kwargs)
    else:
        form = Form(*args, **kwargs)
    if _request.is_ajax():
        raise AjaxDataException({'errors': form.errors.as_json(), 'valid': not form.errors})
    return form
