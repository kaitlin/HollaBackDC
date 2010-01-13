"""
Tagging related views.
"""
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from tagging.models import Tag, TaggedItem
from tagging.utils import get_tag_list, get_queryset_and_model


def tagged_object_list(request, queryset=None, tags=None, related_tags=False,
                       related_tag_counts=True, union=True, **kwargs):
    """
    A thin wrapper around
    ``django.views.generic.list_detail.object_list`` which creates a
    ``QuerySet`` containing instances of the given queryset or model
    tagged with the given tag.

    In addition to the context variables set up by ``object_list``, a
    ``tag`` context variable will contain the ``Tag`` instance for the
    tag.

    If ``related_tags`` is ``True``, a ``related_tags`` context variable
    will contain tags related to the given tag for the given model.
    Additionally, if ``related_tag_counts`` is ``True``, each related
    tag will have a ``count`` attribute indicating the number of items
    which have it in addition to the given tag.

    If ``union`` is ``True``, will return list of objects, which are marked
    by one of mentioned tags. In other case will return list of object, which
    are marked by all of mentioned tags.
    """
    tag_instances = get_tag_list(tags)
    if not tag_instances:
        raise Http404
    if union:
        qs_func = TaggedItem.objects.get_union_by_model
    else:
        qs_func = TaggedItem.objects.get_intersection_by_model
    if not kwargs.has_key('extra_context'):
        kwargs['extra_context'] = {}
    kwargs['extra_context']['union'] = union
    if tag_instances:
        queryset = qs_func(queryset, tag_instances)
        kwargs['extra_context']['tags'] = tag_instances
        if related_tags:
            kwargs['extra_context']['related_tags'] = \
                Tag.objects.related_for_model(tag_instances, queryset,
                                              counts=related_tag_counts)
    else:
        queryset = get_queryset_and_model(queryset)[0]
    return object_list(request, queryset, **kwargs)
