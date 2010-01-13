# -*- coding: utf-8 -*-
# (c) 2008 Alberto Paro <alberto@ingparo.it>
#          Alexander Solovyov
#

import os
from datetime import datetime
from time import strptime, mktime
from xmlrpclib import Fault, Boolean

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings

from lib.helpers import reverse
from blog.models import Post
from xmlrpc.utils import signature
from tagging.models import Tag


def auth_user(username, password):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        try:
            u = User.objects.get(email=username)
        except User.DoesNotExist:
            return False
    return u.check_password(password) and u.is_superuser


def datetime_from_iso(isostring):
    return datetime.fromtimestamp(mktime(strptime(isostring,
                                                  '%Y%m%dT%H:%M:%SZ')))

def datetime_from_content(content):
    if 'dateCreated' in content:
        return datetime_from_iso(str(content['dateCreated']))
    return datetime.now()

def tags(content):
    tags = content.get('mt_keywords', content.get('categories'))
    if isinstance(tags, list):
        return ' '.join(tags)
    return tags

def post_struct(post):
    return {'userid': post.author.username,
            'pubDate': post.date.isoformat(),
            'postid': str(post.id),
            'description': post.text,
            'title': post.name,
            'link': post.get_absolute_url(),
            'permalink': post.get_absolute_url(),
            'mt_allow_comments': int(post.enable_comments),
            'mt_keywords': [tag_struct(tag) for tag in post.get_tag_objects()]}


def tag_struct(tag):
    return {'name': tag.name,
            'description': tag.name,
            'htmlUrl': tag.get_absolute_url(),
            'rssUrl': reverse('feed', 'tag/%s' % tag.name)}


###
### Blogger API
###

@signature(str, str, str)
def blogger_getUsersBlogs(appkey, username, password):
    """
    Get all user blogs.

    Arguments
    ~~~~~~~~~
    * appkey string (application key)
    * utente string (user name)
    * password string (user password)

    Return value
    ~~~~~~~~~~~~
    * an array of <struct>'s containing the ID (blogid), name (blogName), and URL (url) of each blog.
    """
    if not auth_user(username, password):
        raise Fault(-1, "Authentication Failure")
    site = Site.objects.get_current()
    return [{'url': 'http://%s/' % site.domain,
             'blogid': Site.objects.get_current().domain,
             'blogName': Site.objects.get_current().name},]

@signature(str, str, str, int, bool)
def blogger_deletePost(appkey, postid, username, password, publish):
    """
    Delete a post.

    Arguments
    ~~~~~~~~~
    * appkey string (application key)
    * postid integer (id of post)
    * username string (user name)
    * password string (user password)
    * publish bool (user password)

    Return value
    ~~~~~~~~~~~~
    * a boolean.
    """
    if not auth_user(username, password):
        raise Fault(-1, "Authentication Failure")

    try:
        b = Post.objects.get(pk = postid)
        b.is_draft = True
        b.save()
        return Boolean(True)
    except Post.DoesNotExist:
        raise Fault(-2, "Post does not exist")
    except Exception, e:
        raise Fault(-255, "Failed to create new post: %s" % str(e))


###
### MetaWeblog API
###

@signature(str, str, str)
def metaWeblog_getCategories(username, password, blogid):
    """
    The struct returned contains one struct for each category, containing
    the following elements: description, htmlUrl and rssUrl.
    This entry-point allows editing tools to offer category-routing as a feature.

    Arguments
    ~~~~~~~~~
    * username string (user name)
    * password string (user password)
    * blogid string (id of blof)

    Return value
    ~~~~~~~~~~~~
    * a list.
    """
    tags = Tag.objects.all()
    return [tag_struct(tag) for tag in tags]


@signature(str, str, int, dict, bool)
def metaWeblog_newPost(blogid, username, password, content, publish):
    """
    Creating a new post.

    Arguments
    ~~~~~~~~~
    * username string (user name)
    * password string (user password)
    * blogid string (id of blog)
    * content dict (content of blog)
    * publish boolean (publish this post?)

    Return value
    ~~~~~~~~~~~~
    * a string id of a post.
    """

    if not auth_user(username, password):
        return Fault(-1, "Authentication Failure")

    try:
        u = User.objects.get(username=username)
        post = Post(name=content['title'],
                    text=content['description'],
                    date=datetime_from_content(content),
                    author=u,
                    is_draft=not publish,
                    site=Site.objects.get_current(),
                    render_method=settings.RENDER_METHOD)

        post.enable_comments = bool(content.get('mt_allow_comments', True))
        post.tags = tags(content)
        if 'mt_pingable' in content:
            pass # TODO
    except Exception, e:
        import traceback
        traceback.print_exc()
        raise Fault(-255, 'Unknown Error: %s' % str(e))

    try:
        post.save()
        return str(post.id)
    except Exception, e:
        raise Fault(-255, "Failed to create new post: %s" % str(e))


@signature(int, str, str, dict, bool)
def metaWeblog_editPost(postid, username, password, content, publish):
    """
    Edit a new post.

    Arguments
    ~~~~~~~~~
    * postid integer (id of post)
    * username string (user name)
    * password string (user password)
    * content dict (content of blog)
    * publish boolean (publish this post?)

    Return value
    ~~~~~~~~~~~~
    * a string id of a post.
    """
    if not auth_user(username, password):
        raise Fault(-1, "Authentication Failure")

    try:
        post = Post.objects.get(id=postid)
        post.name = content['title']
        post.text = content['description']
        post.date = datetime_from_content(content)
        post.is_draft = not bool(publish)
        post.enable_comments = bool(content.get('mt_allow_comments', True))
        if 'mt_pingable' in content:
            pass # TODO
        post.tags = tags(content)
        post.save()
        return str(post.id)
    except Post.DoesNotExist:
        raise Fault(-2, "Post does not exist")
    except Exception, e:
        raise Fault(-255, "Failed to create new post: %s" % str(e))


@signature(int, str, int)
def metaWeblog_getPost(postid, username, password):
    """
    Get a post.

    Arguments
    ~~~~~~~~~
    * postid integer (id of post)
    * username string (user name)
    * password string (user password)

    Return value
    ~~~~~~~~~~~~
    * a struct.
    """
    if not auth_user(username, password):
        return Fault(-1, "Authentication Failure")

    try:
        post = Post.objects.get(pk=postid)
        return post_struct(post)
    except Post.DoesNotExist:
        raise Fault(-2, "Post does not exist")
    except Exception, e:
        raise Fault(-255, 'Unknown Exception: %s' % str(e))


@signature(str, str, str, int)
def metaWeblog_getRecentPosts(blogid, username, password, numberOfPosts):
    """
    Get a lot of recent posts.

    Arguments
    ~~~~~~~~~
    * blogid string (id of blog)
    * username string (user name)
    * password string (user password)
    * numberOfPosts integer (number of post)

    Return value
    ~~~~~~~~~~~~
    * a list of structs.
    """
    if not auth_user(username, password):
        return Fault(-1, "Authentication Failure")

    try:
        posts = Post.all_objects.order_by('-date')[:numberOfPosts]
        return [post_struct(p) for p in posts]
    except Exception, e:
        raise Fault(-255, 'Unknown Exception: %s' % str(e))


@signature(str, str, str, dict)
def metaWeblog_newMediaObject(blogid, username, password, fileObject):
    """
    Create a new media object.

    Arguments
    ~~~~~~~~~
    * blogid string (id of blog)
    * username string (user name)
    * password string (user password)
    * fileObject struct (fileobject)

    Return value
    ~~~~~~~~~~~~
    * a string.
    """
    # The input struct must contain at least three elements, name,
    # type and bits. returns struct, which must contain at least one
    # element, url
    if not auth_user(username, password):
        raise Fault(-1, "Authentication Failure")

    file_data = str(fileObject['bits'])
    file_name = str(fileObject['name'])
    dated_path = datetime.datetime.now().strftime('%Y_%m_%d_') + os.path.basename(file_name)
    relative_path = os.path.join('upload', dated_path)
    target_path = os.path.abspath(os.path.join(settings.STATIC_ROOT, relative_path))
    target_url = os.path.abspath(settings.STATIC_ROOT, relative_path)
    open(target_path, 'w').write(file_data)
    return target_url
