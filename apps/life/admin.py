from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from lib import libadmin
from life.models import LifeFlow


class LifeFlowAdmin(libadmin.BFAdmin):
    prepopulated_fields = {'slug': ('name', )}
    list_display = ('name', 'feed', 'link', 'source', 'active')
    search_fields = ('name', 'feed', 'link')
    exclude = ('etag', 'bad_dates', 'bad_tags', 'target', 'owner')
    fieldsets = (
        (None, {'fields': ('link', 'name', 'slug', 'feed')}),
        (_('Multiuser/multisite support'), {'classes': ('collapse',),
                                            'fields': ('author', 'site',)}),
    )

admin.site.register(LifeFlow, LifeFlowAdmin)
