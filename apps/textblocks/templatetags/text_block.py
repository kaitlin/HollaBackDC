# -*- coding: utf-8

from django import template
from textblocks.models import TextBlock

register = template.Library()

@register.inclusion_tag('templatetags/text_block.html')
def text_block(code):
    try:
        return {'text_block': TextBlock.objects.get(code=code) }
    except TextBlock.DoesNotExist:
        return {'text_block': {'html': ''}}
