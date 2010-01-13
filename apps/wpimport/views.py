import uuid

from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseRedirect

from accounts.models import ActionRecord
from lib.decorators import render_to
from wpimport.models import WPost, Comment
from blog.models import Post
from discussion.models import CommentNode

staff_required = user_passes_test(lambda u: getattr(u, 'is_staff', False))


@staff_required
def post_list(request, **kwargs):
    kwargs['queryset'] = WPost.objects.all()
    return object_list(request, **kwargs)


def _save_comment(comment_id, new_post, old_post):
    comment = Comment.objects.get(pk=comment_id)
    if not comment.post == old_post:
        raise ValueError("this comment does not belong to this post")
    try:
        user = User.objects.get(email__iexact=comment.author_email)
    except User.DoesNotExist:
        user = ActionRecord.objects.create_user(
            name=comment.author,
            email=comment.author_email,
            password=uuid.uuid4().hex[:10],
            send_email=False,
            site=comment.author_url)
    new = CommentNode(
        user=user,
        pub_date=comment.date,
        body_html=comment.content,
        approved=True,
        object=new_post,
        )
    new.save()
    return new


@staff_required
@render_to('wpimport/post_detail.html')
def post_detail(request, object_id):
    post = get_object_or_404(WPost, pk=object_id)
    try:
        imported = Post.objects.get(slug=post.slug)
    except Post.DoesNotExist:
        imported = None
    if request.method == 'POST' and not imported:
        settings.ENABLE_PINGBACK = False
        # TODO: remove hardcoded author
        author = User.objects.get(pk=1)
        new = Post(
            author=author,
            name=post.title,
            slug=post.slug,
            text=post.content,
            date=post.date,
            enable_comments = post.comment_status == 'open',
            tags = ' '.join(c.name for c in post.categories.all()),
            )
        new.save()
        request.user.message_set.create(message="Post #%s with slug %s added" % (post.id, post.slug))
        for c_id in request.POST.getlist('comment'):
            cmt = _save_comment(c_id, new, post)
            request.user.message_set.create(message="Comment #%s from %s has been added" % (cmt.id, cmt.user))
        return HttpResponseRedirect(post.get_absolute_url())
    return {'object': post, 'imported': imported}
