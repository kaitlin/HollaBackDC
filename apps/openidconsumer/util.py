import time
import base64
from hashlib import md5
import operator

try:
    from openid.yadis import xri
except ImportError:
    raise Exception("python-openid >= 2.0.0 is required!")
import openid.store
from openid.store.interface import OpenIDStore
from openid.association import Association as OIDAssociation
from django.conf import settings
from django.db.models.query import Q

from openidconsumer.models import Association, Nonce

class OpenID:
    def __init__(self, openid, issued, attrs=None, sreg=None):
        self.openid = openid
        self.issued = issued
        self.attrs = attrs or {}
        self.sreg = sreg or {}
        self.is_iname = (xri.identifierScheme(openid) == 'XRI')

    def __repr__(self):
        return '<OpenID: %s>' % self.openid

    def __str__(self):
        return self.openid

class DjangoOpenIDStore(OpenIDStore):
    def __init__(self):
        self.max_nonce_age = 6 * 60 * 60 # Six hours

    def storeAssociation(self, server_url, association):
        assoc = Association(
            server_url = server_url,
            handle = association.handle,
            secret = base64.encodestring(association.secret),
            issued = association.issued,
            lifetime = association.issued,
            assoc_type = association.assoc_type
        )
        assoc.save()

    def getAssociation(self, server_url, handle=None):
        if handle is not None:
            assocs = Association.objects.filter(server_url=server_url, handle=handle)
        else:
            assocs = Association.objects.filter(server_url = server_url)
        if not assocs:
            return None
        associations = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc.handle, base64.decodestring(assoc.secret), assoc.issued,
                assoc.lifetime, assoc.assoc_type
            )
            if association.getExpiresIn() == 0:
                self.removeAssociation(server_url, assoc.handle)
            else:
                associations.append((association.issued, association))
        if not associations:
            return None
        return associations[-1][1]

    def removeAssociation(self, server_url, handle):
        assocs = Association.objects.filter(server_url=server_url, handle=handle)
        assocs_exist = assocs.count() > 0
        assocs.delete()
        return assocs_exist

    def useNonce(self, server_url, timestamp, salt):
        if abs(timestamp - time.time()) > openid.store.nonce.SKEW:
            return False
        query = (Q(server_url__exact=server_url),
                 Q(timestamp__exact=timestamp),
                 Q(salt__exact=salt),
                 )
        try:
            ononce = Nonce.objects.get(reduce(operator.and_, query))
        except Nonce.DoesNotExist:
            ononce = Nonce(server_url=server_url,
                           timestamp=timestamp,
                           salt=salt
                           )
            ononce.save()
            return True
        else:
            ononce.delete()
            return False

    def cleanupNonce(self):
        skew = openid.store.nonce.SKEW
        Nonce.objects.filter(timestamp__lte=int(time.time()) - skew).delete()

    def cleaupAssociations(self):
        Association.objects.extra(where=['issued + lifetimeint<(%s)' % time.time()]).delete()

    def getAuthKey(self):
        # Use first AUTH_KEY_LEN characters of md5 hash of SECRET_KEY
        return md5(settings.SECRET_KEY).hexdigest()[:self.AUTH_KEY_LEN]

    def isDumb(self):
        return False

def from_openid_response(openid_response):
    issued = int(time.time())
    return OpenID(
        openid_response.identity_url, issued, openid_response.signed_fields,
        openid_response.extensionResponse('sreg', False)
    )
