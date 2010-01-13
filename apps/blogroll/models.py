# -*- mode: python; coding: utf-8; -*-

"""
Django application that allows to create XFN-compatible block of links
"""

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from blogroll.relations import *


class Link(models.Model):
    user = models.ForeignKey(User, related_name='blogroll', blank=True, null=True)
    site = models.ForeignKey(Site, related_name='blogroll')
    url = models.URLField(_('URL'), verify_exists=False, blank=True)
    name = models.CharField(_('Name'), max_length=100, blank=True)
    relations = models.CharField(_('Relations'), max_length=100, blank=True, editable=False)
    weight = models.IntegerField(_('Weight'), blank=True, default=0, help_text=_(u'You can order links by this field. Link with smaller number goes first.'))

    friendship_rel = models.CharField(_('Friendship relation'), max_length=20, choices=FRIENDSHIP_REL, blank=True)
    physical_rel = models.CharField(_('Physical relation'), max_length=20, choices=PHYSICAL_REL, blank=True)
    professional_rel =  models.CharField(_('Profesional relation'), max_length=20, choices=PROFESSIONAL_REL, blank=True)
    geographical_rel = models.CharField(_('Geographical relation'), max_length=20, choices=GEOGRAPHICAL_REL, blank=True)
    family_rel = models.CharField(_('Family relation'), max_length=20, choices=FAMILY_REL, blank=True)
    romantic_rel = models.CharField(_('Romantic relation'), max_length=20, choices=ROMANTIC_REL, blank=True)
    identity_rel = models.CharField(_('Identity relation'), max_length=20, choices=IDENTITY_REL, blank=True)

    class Meta:
        ordering = ['weight']
        verbose_name = _('Link')
        verbose_name_plural = _('Links')

    def __unicode__(self):
        return self.name

    def save(self):
        """
        Cache all not empty relations in single relations field
        """

        rels = ['friendship_rel', 'physical_rel', 'professional_rel',
                'geographical_rel', 'family_rel', 'romantic_rel', 'identity_rel']
        self.relations = ' '.join(filter(lambda x: x != '', [getattr(self, x) for x in rels]))
        if not self.name:
            self.name = self.user.name or self.user.username

        if not self.url:
            self.url = self.user.site

        super(self.__class__, self).save()
