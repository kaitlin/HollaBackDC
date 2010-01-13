# This module must be imported somewhere to work

import settings
import traceback

from django.template import Context, loader, Template, TemplateDoesNotExist
from django.core.mail import mail_admins
from django.contrib.sites.models import Site

from discussion.models import CommentNode
from watchlist.models import Subscription
from lib.helpers import signals


DEFAULT_COMMENT_SUBJECT = '''New comment for {{ comment.content_type }} "{{ obj.name }}"'''
DEFAULT_COMMENT_BODY = '''Author: {{ comment.user.first_name|default:comment.user.username }}

Comment text:
{{ comment.mail_body|safe }}

Reply: {{ site_url }}{{ comment.get_absolute_url }}

You can unsubscribe at: {% load watchlist_tags %}{{ site_url }}{% unsubscribe_url comment.object %}'''


@signals.post_save(sender=CommentNode)
def send_comment_by_mail(instance, created, **kwargs):
    """
    Send email notification to all comments subscribers.

    Do this only if comment was created (and is approved) or became approved.
    Uses two templates (there is fallbacks in case of template absence:

     - ``comment_subject.txt`` (fallback: ``DEFAULT_COMMENT_SUBJECT``)
     - ``comment_body.txt`` (fallback: ``DEFAULT_COMMENT_BODY``)
    """
    if created and not instance.approved:
        return
    if not created and not getattr(instance, 'send_notification', False):
        return
    comment = instance
    obj = comment.object
    if getattr(obj, 'is_draft', False):
        return

    # use templates for mail subject and body
    try:
        subject_tmp = loader.get_template("comment_subject.txt")
    except TemplateDoesNotExist:
        subject_tmp = Template(DEFAULT_COMMENT_SUBJECT)
    try:
        body_tmp = loader.get_template("comment_body.txt")
    except TemplateDoesNotExist:
        body_tmp = Template(DEFAULT_COMMENT_BODY)

    current_domain = Site.objects.get_current()
    site_url = '%s://%s' % (settings.SITE_PROTOCOL, current_domain)
    ctx = Context({'obj': obj, 'comment': comment, 'site_url': site_url})
    subject = subject_tmp.render(ctx).strip()
    body = body_tmp.render(ctx).strip()

    # send email to the user
    try:
        for user in Subscription.objects.get_subscribers(obj, exclude=(comment.user, )):
            if user.email:
                user.email_user(subject, body)
    except UnicodeEncodeError:
        if not settings.DEBUG:
            mail_admins("Trouble while sending email", traceback.format_exc())
        else:
            raise

@signals.pre_save(sender=CommentNode)
def check_comment(instance, **kwargs):
    """
    Check if comment was already present in database and became approved.
    """
    try:
        original = CommentNode.objects.get(pk=instance.pk)
    except CommentNode.DoesNotExist:
        return
    if instance.approved and not original.approved:
        instance.send_notification = True
