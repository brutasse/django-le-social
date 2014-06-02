import base64
import operator
import time

from functools import reduce
from hashlib import md5

try:
    from openid.association import Association as OIDAssociation
    from openid.store import nonce
    from openid.store.interface import OpenIDStore
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        "python-openid is required to use le_social.openid"
    )

from django.conf import settings
from django.db.models import Q

from .models import Association, Nonce


class DjangoOpenIDStore(OpenIDStore):
    def __init__(self):
        self.max_nonce_age = 6 * 60 * 60  # Six hours

    def storeAssociation(self, server_url, association):
        Association.objects.create(
            server_url=server_url,
            handle=association.handle,
            secret=base64.encodestring(association.secret),
            issued=association.issued,
            lifetime=association.lifetime,
            assoc_type=association.assoc_type,
        )

    def getAssociation(self, server_url, handle=None):
        assocs = []
        if handle is not None:
            assocs = Association.objects.filter(
                server_url=server_url, handle=handle,
            )
        else:
            assocs = Association.objects.filter(server_url=server_url)
        if not assocs:
            return None
        associations = []
        expired = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc.handle, base64.decodestring(assoc.secret), assoc.issued,
                assoc.lifetime, assoc.assoc_type,
            )
            if association.getExpiresIn() == 0:
                expired.append(assoc)
            else:
                associations.append((association.issued, association))

        for assoc in expired:
            assoc.delete()
        if not associations:
            return None
        associations.sort()
        return associations[-1][1]

    def removeAssociation(self, server_url, handle):
        assocs = list(Association.objects.filter(
            server_url=server_url, handle=handle,
        ))
        assocs_exist = len(assocs) > 0
        for assoc in assocs:
            assoc.delete()
        return assocs_exist

    def useNonce(self, server_url, timestamp, salt):
        if abs(timestamp - time.time()) > nonce.SKEW:
            return False

        query = [
            Q(server_url__exact=server_url),
            Q(timestamp__exact=timestamp),
            Q(salt__exact=salt),
        ]
        try:
            Nonce.objects.get(reduce(operator.and_, query))
        except Nonce.DoesNotExist:
            Nonce.objects.create(
                server_url=server_url,
                timestamp=timestamp,
                salt=salt,
            )
            return True
        return False

    def cleanupNonces(self, _now=None):
        if _now is None:
            _now = int(time.time())
        limit = _now - nonce.SKEW
        expired = Nonce.objects.filter(timestamp__lt=limit)
        count = expired.count()
        if count:
            expired.delete()
        return count

    def cleanupAssociations(self):
        now = int(time.time())
        expired = Association.objects.extra(
            where=['issued + lifetime < %d' % now])
        count = expired.count()
        if count:
            expired.delete()
        return count

    def getAuthKey(self):
        return md5(settings.SECRET_KEY).hexdigest()[:self.AUTH_KEY_LEN]

    def isDumb(self):
        return False
