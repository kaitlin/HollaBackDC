from django.contrib import databrowse, admin

from wpimport.models import Comment, Category, WPost, User


databrowse.site.register(Comment)
databrowse.site.register(Category)
databrowse.site.register(WPost)
databrowse.site.register(User)

admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(WPost)
admin.site.register(User)
