from django.template import Library
from friends.models import FriendBlog

register = Library()

@register.inclusion_tag('friends/sidebar.html', takes_context=True)
def friends_sidebar(context):
    return {
            'STATIC_URL': context['STATIC_URL'],
            'request': context['request'],
            'friends': FriendBlog.objects.active(),
            'settings': context['settings'],
            }
