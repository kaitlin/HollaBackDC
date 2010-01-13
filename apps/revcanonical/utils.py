from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from revcanonical.baseconv import base62


def encode(obj):
    ctype = ContentType.objects.get_for_model(obj)
    return '%s.%s' % tuple(map(base62.from_decimal, [ctype.pk, obj.pk]))


def decode(addr):
    ctype_pk, obj_pk = map(base62.to_decimal, addr.split('.'))
    ctype = get_object_or_404(ContentType, pk=ctype_pk)
    obj = get_object_or_404(ctype.model_class(), pk=obj_pk)
    return obj
