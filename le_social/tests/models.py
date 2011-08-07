from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template import loader

from le_social.registration import models as registration_models


class BaseRegistrationProfile(registration_models.RegistrationProfile):
    user = models.ForeignKey(User)

    class Meta:
        abstract = True


class RegistrationProfile(BaseRegistrationProfile):
    def send_notification(self, **kwargs):
        """Kinda useless but no notification"""
        pass


class NotifyRegistrationProfile(BaseRegistrationProfile):
    def send_notification(self, **kwargs):
        send_mail('Account activation', loader.render_to_string(
            'le_social/registration/activation_email.txt',
        ), 'no-reply@example.com', [self.user.email])


class ExpiringRegistrationProfile(BaseRegistrationProfile):
    def activation_key_expired(self, **kwargs):
        return True
