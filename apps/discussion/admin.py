# -*- mode: python; coding: utf-8; -*-

from django.core.urlresolvers import reverse as urlreverse
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin

from discussion.models import CommentNode


class CommentNodeAdmin(admin.ModelAdmin):
    list_display = ('get_clean_html', 'user', 'pub_date', 'content_type',
                    'object_id', 'reply_to_id', 'approved')
    list_filter = ('approved',)
    list_search = ('user',)
    actions = ['comment_approve']

    def comment_approve(self, request, queryset):
        count = queryset.update(approved=True)
        msg = (count == 1) and _('One comment was approved') or (_('%d comments were approved') % count)
        self.message_user(request, msg[:])
    comment_approve.short_description = _('Mark selected comments as approved')

    def get_form(self, request, obj=None, **kwargs):
        form_cls = super(CommentNodeAdmin, self).get_form(request, obj, **kwargs)

        if obj is not None: # additional interface features in admin
            if obj.object_id and obj.content_type: # link to parent object
                object_url = urlreverse('admin', args=['%s/%s/%d' % (obj.content_type.app_label, obj.content_type.model, obj.object_id)])
                form_cls.base_fields['object_id'].help_text += u'| <a href="%s">%s</a> |' % (object_url, _('Parent object'))

            if obj.reply_to_id: # link to reply_to comment node
                comment_url = urlreverse('admin', args=['discussion/CommentNode/%d/' % obj.reply_to_id])
                form_cls.base_fields['object_id'].help_text += u'| <a href="%s">%s</a> |' % (comment_url, _('Parent comment'))

        return form_cls

admin.site.register(CommentNode, CommentNodeAdmin)
