from django.contrib import admin

from textblocks.models import TextBlock

class TextBlockAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'comment',)
    search_fields = ('name', 'text')

admin.site.register(TextBlock, TextBlockAdmin)
