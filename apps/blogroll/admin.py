# -*- mode: python; coding: utf-8; -*-

from django.contrib import admin

from blogroll.models import Link


class LinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'relations', 'weight')

admin.site.register(Link, LinkAdmin)
