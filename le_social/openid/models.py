from django.db import models
from django.utils.translation import ugettext_lazy as _


class Nonce(models.Model):
    server_url = models.CharField(_('Server URL'), max_length=255)
    timestamp = models.IntegerField(_('Timestamp'))
    salt = models.CharField(_('Salt'), max_length=40)

    def __unicode__(self):
        return u'Nonce: %s' % self.pk


class Association(models.Model):
    server_url = models.CharField(_('Server URL'), max_length=2047)
    handle = models.CharField(_('OpenID handle'), max_length=255)
    secret = models.CharField(_('OpenID secret'), max_length=255)
    issued = models.IntegerField(_('Issued'))
    lifetime = models.IntegerField(_('Lifetime'))
    assoc_type = models.CharField(_('Association type'), max_length=64)

    def __unicode__(self):
        return u'Association: %s, %s' % (self.server_url, self.handle)
