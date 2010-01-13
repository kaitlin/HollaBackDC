#Based on Djangoid by Nicolas Trangez <ikke nicolast be>
# (c) Leschinsky Oleg <helge@leschinsky.in.ua>

from django.db import models
from django.contrib.auth.models import User


# These are some dumb mappings of the original OpenID store tables as used
# by the SQLStore implementation(s).
# They're used by "DjangoidStore"
class OidStoreNonce(models.Model):
    nonce = models.CharField(max_length=8, primary_key=True)
    expires = models.IntegerField()


class OidStoreAssociation(models.Model):
    server_url = models.CharField(max_length = 255)
    handle = models.CharField(max_length=78)
    secret = models.TextField()
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.CharField(max_length=64)

    class Meta:
        unique_together = (("server_url", "handle"),)


class OidStoreSetting(models.Model):
    setting = models.CharField(max_length = 128, primary_key=True)
    value = models.TextField()


class TrustedRoot(models.Model):
    "Represent one trusted root URI. Can be shared between several users."
    root = models.URLField("Trusted root URI", unique=True, verify_exists=False)

    def __str__(self):
        return self.root


class DjangoidUser(models.Model):
    user = models.OneToOneField(User, unique=True, primary_key=True)
    trusted_roots = models.ManyToManyField(TrustedRoot, blank=True, null=True,
                                           help_text="URI's trusted by this user")

    def __unicode__(self):
        return self.user.username

    def authenticate(self, root):
        r = TrustedRoot.objects.filter(root=root)
        if len(r) == 0: #Certainly not trusted
            TrustedRoot(root=root).save()
        else:
            return bool(self.trusted_roots.filter(root=root))
