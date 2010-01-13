from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from lib import libadmin
from friends.models import FriendBlog


class FriendBlogAdmin(libadmin.BFAdmin):
    prepopulated_fields = {'slug': ('name', )}
    list_display = ('name', 'feed', 'link', 'active')
    search_fields = ('name', 'feed', 'link')
    exclude = ('etag', 'bad_dates', 'bad_tags', 'target', 'owner')
    fieldsets = (
        (None, {'fields': ('link', 'name', 'slug', 'feed')}),
        (_('Extra'), {'classes': ('collapse',),
                      'fields': ('active', 'weight',)}),
        (_('Multiuser/multisite support'), {'classes': ('collapse',),
                                            'fields': ('author', 'site',)}),
        (_('Relations'), {'classes': ('collapse',),
                          'fields': ('rel_friendship', 'rel_physical',
                                     'rel_professional', 'rel_geographical',
                                     'rel_family', 'rel_romantic',
                                     'rel_identity')}),
    )

admin.site.register(FriendBlog, FriendBlogAdmin)
