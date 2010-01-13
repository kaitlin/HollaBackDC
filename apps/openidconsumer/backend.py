from django.contrib.auth.models import User

from openidconsumer.models import UserAssociation

class OpenidBackend:
    def authenticate(self, openid):
        try:
            ua = UserAssociation.objects.select_related(depth=1).get(openid_url=openid)
            return ua.user
        except UserAssociation.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
