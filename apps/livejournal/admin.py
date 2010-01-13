from django.contrib import admin

from livejournal.models import LiveJournalPost
from livejournal.utils import lj_crosspost, lj_delete
from blog.models import Post
from blog.admin import PostAdmin
from lib.helpers import signals

class LiveJournalPostAdmin(admin.ModelAdmin):
    list_display = ('post', 'need_crosspost')

admin.site.register(LiveJournalPost, LiveJournalPostAdmin)


class LiveJournalPostInlineAdmin(admin.TabularInline):
    model = LiveJournalPost
    max_num = 1

PostAdmin.list_display += ('lj_object', )

pa = admin.site._registry[Post]
pa.inline_instances.append(LiveJournalPostInlineAdmin(pa.model, pa.admin_site))

signals.pre_save(sender=LiveJournalPost)(lj_crosspost)
signals.pre_delete(sender=LiveJournalPost)(lj_delete)
