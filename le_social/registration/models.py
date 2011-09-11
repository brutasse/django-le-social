from django.db import models
from django.utils.translation import ugettext_lazy as _


class RegistrationProfile(models.Model):
    """
    An abstract registration profile. Only provides a queryable
    `activation_key` field and a hook to determine whether the profile
    has expired or not.

    Example usage, to tie it to an actual auth.User object:

    >>> from le_social.registration import models as registration_models
    >>> from django.contrib.auth.models import User
    >>> from django.db import models

    >>> class RegistrationProfile(registration_models.RegistrationProfile):
    ...     user = models.ForeignKey(User)
    """
    ACTIVATED = "ALREADY_ACTIVATED"
    activation_key = models.CharField(_('Activation key'), max_length=40,
                                      db_index=True)

    class Meta:
        abstract = True

    def activation_key_expired(self):
        """
        Simple default behaviour: activation keys never expire.
        Subclasses may override this.
        """
        return False

    def send_notification(self, **kwargs):
        raise NotImplementedError(
            "Subclasses must implement send_notification() for "
            "activation messages",
        )
