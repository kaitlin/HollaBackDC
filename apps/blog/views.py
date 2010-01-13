# -*- mode: python; coding: utf-8; -*-

from datetime import datetime as dt

from django.views.generic.list_detail import object_list
from django.views.generic import date_based
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext as _
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_page

from lib.forms import build_form
from lib.exceptions import RedirectException
from lib.decorators import render_to, ajax_request
from lib.helpers import get_object_or_404_ajax

from accounts.models import ActionRecord
from discussion.forms import CommentForm, AnonymousCommentForm
from discussion.models import CommentNode
from blog.models import Post
from tagging.views import tagged_object_list
from render import render

from django.db.models import Q

def _get_reply_to(request):
    try:
        return int(request.GET.get('reply_to', None))
    except (ValueError, TypeError):
        return None


def post_list(request, *args, **kwargs):
    """Post listing. Only shows posts that are older than now()"""
    if request.user.id:
        # the OR clause includes logged-in user's drafts as well
        q_lookup = (Q(is_draft=False) | Q(author=request.user))
        qs = Post.all_objects.filter(q_lookup).exclude(date__gt=dt.now())
    else:
        qs = Post.objects.all()

    return object_list(request, queryset=qs, *args, **kwargs)


archive_dict = {
    'date_field': 'date',
    'allow_empty': True,
}

def archive_month(request, year, month):
    if int(year) < 1901: # to exclude all troubles with strftime
        raise Http404
    qs = Post.objects.all()
    return date_based.archive_month(request, year, month, queryset=qs,
                                    month_format='%m',
                                    template_name='blog/post_list.html',
                                    **archive_dict)


def archive_year(request, year):
    if int(year) < 1901:
        raise Http404
    qs = Post.objects.all()
    return date_based.archive_year(request, year, make_object_list=True,
                                   queryset=qs,
                                   template_name='blog/post_archive_year.html',
                                   **archive_dict)


def archive_day(request, year, month, day):
    if int(year) < 1901:
        raise Http404
    qs = Post.objects.all()
    return date_based.archive_day(request, year, month, day, month_format='%m',
                                  template_name='blog/post_archive_year.html',
                                  queryset=qs, **archive_dict)


def by_tag(request, tag, *args, **kwargs):
    """Post listing. Only shows posts that belong to specified tags"""
    queryset = Post.objects.all()
    if not kwargs.has_key('extra_context'):
        kwargs['extra_context'] = {}
    kwargs['extra_context']['feedurl'] = 'tag/%s' % tag
    def tagged_objects(taglist, union):
        return tagged_object_list(request, queryset, taglist, union=union,
                                  *args, **kwargs)
    if '+' in tag:
        return tagged_objects(tag.split('+'), False)
    else:
        return tagged_objects(tag.split('|'), True)


def by_author(request, author, *args, **kwargs):
    """Post listing. Only shows posts that were created by specified author"""
    try:
        user = User.objects.get(username__exact=author)
    except User.DoesNotExist:
        raise Http404
    queryset = Post.objects.filter(author=user)
    if not kwargs.has_key('extra_context'):
        kwargs['extra_context'] = {}
    kwargs['extra_context']['feedurl'] = 'author/%s' % user
    kwargs['extra_context']['author'] = user
    kwargs['queryset'] = queryset
    return object_list(request, *args, **kwargs)


@render_to('blog/post_detail.html')
def post_detail(request, year, month, day, slug):
    reply_to = _get_reply_to(request)
    year, month, day = int(year), int(month), int(day)
    filtr = {'slug': slug,
             'date__year': year,
             'date__month': month,
             'date__day': day}
    qs = (request.user.is_staff
	  and Post.all_objects
	  or Post.objects)
    post = get_object_or_404(qs, **filtr)
    if post.comments_open():
        Form = (request.user.is_authenticated()
                and CommentForm
                or AnonymousCommentForm)
        form = build_form(Form, request, post=post, user=request.user,
                          remote_ip=request.META.get('REMOTE_ADDR'),
                          initial={'reply_to': reply_to})
        if form.is_valid():
            c, user_is_new = form.save()
            if not request.user.is_authenticated():
                if user_is_new:
                    c.user.backend = 'django.contrib.auth.backends.ModelBackend'
                    message = _('Please look in your mailbox for info about your account.')
                else:
                    ActionRecord.approvals.send_approval(c)
                    message = _('Please look in your mailbox for comment approval link.')
            else:
                message = None
            raise RedirectException(c.get_absolute_url(), notice_message=message)
    else:
        form = None
    return {
            'object': post,
            'form': form,
            'reply_to': reply_to,
            'feedurl': 'comments/%s' % post.id,
            'site': Site.objects.get_current(),
            'post_detail': True}


@ajax_request
def comment_edit(request, object_id):
    comment = get_object_or_404_ajax(CommentNode, pk=object_id)
    if request.user != comment.user:
        return {'error': {'type': 403, 'message': 'Access denied'}}
    if 'get_body' in request.POST:
        return {'body': comment.body}
    elif 'body' in request.POST:
        comment.body = request.POST['body']
        comment.save()
        return {'body_html': comment.body_html}
    else:
        return {'error': {'type': 400, 'message': 'Bad request'}}


@ajax_request
def comment_delete(request, object_id):
    if not request.user.is_staff:
        return {'error': {'type': 403, 'message': 'Access denied'}}
    comment = get_object_or_404_ajax(CommentNode, pk=object_id)
    if request.POST.get('delete'):
        comment.delete()
        return {'success': True, 'id': object_id}
    else:
        return {'error': {'type': 400, 'message': 'Bad request'}}


@ajax_request
def preview(request):
    return {'body_preview': render(request.POST['body'], settings.RENDER_METHOD)}


def process_root_request(request):
    return HttpResponseRedirect('/%s' % settings.BLOG_URLCONF_ROOT)


@cache_page(60*60*24*30)
def processed_js(request):
    tmpl = loader.get_template('processed.js')
    ctx = RequestContext(request, {})
    return HttpResponse(tmpl.render(ctx), content_type='application/x-javascript')


@render_to('wysiwyg.js')
def wysiwyg_js(request):
    return {}

@render_to('blog/tag_cloud.html')
def tag_cloud(request):
    return {'queryset': Post.objects.all()}

@render_to('blog/featured.html')
def featured(request):
    featured_list = Post.featured_objects.all()
    return {'object_list': featured_list}
