import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from watchlist.managers import SubscriptionManager


class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions')
    date = models.DateTimeField(editable=False, default=datetime.datetime.now)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    objects = SubscriptionManager()

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'), )

    def __unicode__(self):
        return u'%s subscribed to %s %s' % (self.user, self.content_type, self.object)
