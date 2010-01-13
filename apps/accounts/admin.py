# -*- mode: python; coding: utf-8; -*-

from django.core.urlresolvers import reverse as urlreverse
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from accounts.models import ActionRecord
from accounts.forms import BfUserChangeForm

UserAdmin.form = BfUserChangeForm

UserAdmin.fieldsets += (
    ('Byteflow Extensions', {'fields': ('site', 'email_new')}),
    )
UserAdmin.list_display = ('username', 'email', 'first_name', 'is_staff', 'is_active')
UserAdmin.search_fields = ('username', 'first_name', 'email')

def get_form(self, request, obj=None, *args, **kwargs):

    form_cls = super(UserAdmin, self).get_form(request, obj, *args, **kwargs)

    if obj is not None: # additional interface feature for users and commentnodes
        comment_list_url = urlreverse('admin', args=['discussion/commentnode'])
        comment_list_url += '/?q=%s' % obj.username
        form_cls.base_fields['email_new'].help_text += u'<a href="%s">%s</a>' % (comment_list_url, _('Users comments'))

    return form_cls

UserAdmin.get_form = get_form

class ActionRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    search_fields = ['user']
    list_filter = ('user', 'date')

admin.site.register(ActionRecord, ActionRecordAdmin)
