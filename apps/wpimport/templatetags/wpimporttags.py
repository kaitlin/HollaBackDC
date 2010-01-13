from django.template import Library
from django.contrib.auth.models import User

register = Library()

@register.simple_tag
def author_exist(comment):
    try:
        user = User.objects.get(email__iexact=comment.author_email)
    except User.DoesNotExist:
        return ''
    else:
        return '<p><strong>Author exists</strong>: <a href="/admin/auth/user/%s/">%s</a></p>' % (user.id, user)
