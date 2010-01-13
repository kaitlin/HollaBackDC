import xmlrpclib

from django.template import loader
from django.conf import settings
from django.contrib.sites.models import Site

from tagging.models import Tag

LJ_RPC = "http://www.livejournal.com/interface/xmlrpc"


def create_args(local_post, remote_post=None):
    args = {
        "username" : settings.LJ_USERNAME,
        "password" : settings.LJ_PASSWORD,
        "ver" : 1,
        "props" : {
            "opt_backdated" : False,
            "opt_preformatted" : True,
            }
        }

    if local_post:
        date = local_post.date

        domain = Site.objects.get_current().domain
        blog_link = u'<a href="http://%s%s">%s</a>' % (domain, local_post.get_absolute_url(), domain)
        subject = u'%s' % (local_post.name, )

        text = local_post.html.replace('<!--more-->', '<lj-cut>')
        context = {'text': text, 'blog_link': blog_link,}
        body = loader.render_to_string('livejournal/body.txt', context)

        args["props"]["taglist"] = ', '.join(map(str, Tag.objects.get_for_object(local_post)))

        args.update({
            'event': unicode(body),
            'subject': subject,
            'year': date.year,
            'mon': date.month,
            'day': date.day,
            'hour': date.hour,
            'min': date.minute,
            })

    if remote_post:
        args.update({
            'itemid': remote_post.lj_id,
            'security': remote_post.access_level,
            })
        args['props'].update({
            'opt_screening': remote_post.screen_comments,
            'opt_nocomments': remote_post.no_comments,
            })

    return args


def lj_edit(local_post, remote_post):
    server = xmlrpclib.ServerProxy(LJ_RPC)
    response = server.LJ.XMLRPC.editevent(create_args(local_post, remote_post))


def lj_create(local_post, remote_post):
    server = xmlrpclib.ServerProxy(LJ_RPC)
    response = server.LJ.XMLRPC.postevent(create_args(local_post))

    remote_post.lj_id = response.get('itemid')
    # it will be saved as we was called at pre_save


def lj_delete(instance, **kwargs):
    if instance.need_crosspost:
        server = xmlrpclib.ServerProxy(LJ_RPC)
        response = server.LJ.XMLRPC.editevent(create_args(None, instance))


def lj_crosspost(instance, **kwargs):
    post = instance.post
    if not post.is_draft and instance.need_crosspost:
        if instance.lj_id:
            lj_edit(post, instance)
        else:
            lj_create(post, instance)


