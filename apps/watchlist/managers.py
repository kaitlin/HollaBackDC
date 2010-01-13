from django.db import models
from django.contrib.contenttypes.models import ContentType

class SubscriptionManager(models.Manager):
    def get_subscribers(self, obj, exclude=()):
        ctype = ContentType.objects.get_for_model(obj)
        qs = self.filter(content_type=ctype, object_id=obj.pk).select_related(depth=1)
        return [i.user for i in qs if i.user not in exclude]

    def subscribe(self, user, obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.get_or_create(user=user, content_type=ctype, object_id=obj.pk)[0]

    def unsubscribe(self, user, obj):
        ctype = ContentType.objects.get_for_model(obj)
        try:
            return self.get(user=user, content_type=ctype, object_id=obj.pk).delete()
        except self.model.DoesNotExist:
            return False