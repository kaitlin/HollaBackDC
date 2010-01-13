# -*- mode: python; coding: utf-8; -*-

from django.contrib import admin
from django.conf import settings
from lib import libadmin
from blog.models import Post


class PostAdmin(libadmin.BFAdmin):
    prepopulated_fields = {'slug': ('name', )}
    list_display = ('name', 'date', 'author', 'enable_comments',
                    'comments_open', 'is_draft', 'site', 'view_link')
    search_fields = ('name', 'text')
    list_filter = ('date', 'is_draft', 'site')
    fieldsets = (
        (None, {'fields': (('author', 'site'),
                           ('name', 'slug'),
                           'tags', 'text', 'render_method', 'date',
                           ('is_draft', 'enable_comments'))}),
        )

    class Media:
        js = ['http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js']
        if settings.WYSIWYG_ENABLE:
            js.extend(
                [settings.STATIC_URL + 'js/wymeditor/jquery.wymeditor.pack.js',
                '/' + settings.BLOG_URLCONF_ROOT + 'wysiwyg_js/'])
        elif settings.RENDER_METHOD in ('html', 'markdown', 'rst'):
            js.append(settings.STATIC_URL + 'js/postimage.js')

admin.site.register(Post, PostAdmin)
