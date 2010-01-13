from django.contrib import admin

from openidconsumer.models import UserAssociation

class UserAssociationAdmin(admin.ModelAdmin):
    list_display = ('openid_url', 'user')
    search_fields = ('openid_url', 'user')

admin.site.register(UserAssociation, UserAssociationAdmin)
