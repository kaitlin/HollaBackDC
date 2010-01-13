# -*- mode: python; coding: utf-8; -*-

from django import template

from discussion.models import CommentNode

register = template.Library()

# Tags

class CommentCountsForObjectsNode(template.Node):
    def __init__(self, objects, context_var):
        self.objects = objects
        self.context_var = context_var

    def render(self, context):
        try:
            objects = template.resolve_variable(self.objects, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = CommentNode.objects.get_counts_in_bulk(objects)
        return ''

class CommentTreeForObjectNode(template.Node):
    def __init__(self, obj, context_var):
        self.obj = obj
        self.context_var = context_var

    def render(self, context):
        try:
            obj = template.resolve_variable(self.obj, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = CommentNode.objects.tree_for_object(obj)
        return ''

def do_comment_counts_for_objects(parser, token):
    """
    Retrieves the total number of comments made for a list of objects
    and stores them in a context variable.

    Example usage::

        {% comment_counts_for_objects widget_list as comment_count_dict %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return CommentCountsForObjectsNode(bits[1], bits[3])

def do_comment_tree_for_object(parser, token):
    """
    Retrieves the comment tree for an object and stores it in a
    context variable.

    Example usage::

        {% comment_tree_for_object widget as comments %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return CommentTreeForObjectNode(bits[1], bits[3])

register.tag('comment_counts_for_objects', do_comment_counts_for_objects)
register.tag('comment_tree_for_object', do_comment_tree_for_object)
