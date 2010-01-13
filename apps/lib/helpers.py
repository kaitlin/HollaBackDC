# -*- mode: python; coding: utf-8; -*-

from urlparse import urlsplit, urlunsplit

from django.db.models import signals as signalmodule
from django.core.urlresolvers import reverse as _reverse
from django.shortcuts import _get_queryset, get_object_or_404
from django.http import Http404
from django.contrib.sites.models import Site

from lib.exceptions import Ajax404


def reverse(view_name, *args, **kwargs):
    return _reverse(view_name, args=args, kwargs=kwargs)


def absolutize_uri(request, local_url):
    request_url = urlsplit(request.build_absolute_uri(local_url))
    absolute_url = urlunsplit(request_url[:1] + (Site.objects.get_current().domain,) + request_url[2:])
    return absolute_url


def get_object_or_404_ajax(*args, **kwargs):
    try:
        return get_object_or_404(*args, **kwargs)
    except Http404, e:
        raise Ajax404, e


def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


class Signals(object):
    '''
    Convenient wrapper for working with Django's signals (or any other
    implementation using same API).

    Example of usage::

       signals.register_signal(siginstance, signame)

       # connect to registered signal
       @signals.signame(sender=YourModel)
       def sighandler(instance, **kwargs):
           perform(instance)

       # connect to any signal
       @signals(siginstance, sender=YourModel)
       def sighandler(instance, **kwargs):
           perform(instance)

    In any case defined function will remain as is, without any changes.

    (c) 2009 Alexander Solovyov, new BSD License
    '''
    def __init__(self):
        self._signals = {}

    def __getattr__(self, name):
        return self._connect(self._signals[name])

    def __call__(self, signal, **kwargs):
        def inner(func):
            signal.connect(func, **kwargs)
            return func
        return inner

    def _connect(self, signal):
        def wrapper(**kwargs):
            return self(signal, **kwargs)
        return wrapper

    def register_signal(self, signal, name):
        self._signals[name] = signal

signals = Signals()

# register all Django's default signals
for k, v in signalmodule.__dict__.iteritems():
    # that's hardcode, but IMHO it's better than isinstance
    if not k.startswith('__') and k != 'Signal':
        signals.register_signal(v, k)
