from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from render import render, RENDER_METHODS


class TextBlock(models.Model):
    code = models.CharField(_(u'Unique system code'), max_length=128, unique=True,
        help_text=_(u'The key attribute'))
    name = models.CharField(_(u'Block name'), max_length=255, blank=True,
        help_text=_(u'The name is renders as h4 (if it is not blank)'))
    text = models.TextField(_(u'Block content'), blank=True)
    render_method = models.CharField(_(u'Render method'), max_length=15,
        choices=RENDER_METHODS, default=settings.RENDER_METHOD)
    html = models.TextField(_(u'HTML'), blank=True, editable=False)
    comment = models.TextField(_(u'Comments about block'), blank=True, max_length=255,
        help_text=_(u'The comment on text block is shown only in admin interface'))
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "updated_on"
        ordering = ['-created_on']

    def __unicode__(self):
        return "%s - %s" % (self.code, self.comment)

    def save(self):
        self.text = self.text.strip()
        #if not self.render_method:
            #self.render_method = settings.RENDER_METHOD
        self.html = render(self.text, self.render_method, unsafe=True)
        super(TextBlock, self).save()
