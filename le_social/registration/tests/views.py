from django.contrib.sites.models import RequestSite

from .. import views
from .models import (RegistrationProfile, NotifyRegistrationProfile,
                     ExpiringRegistrationProfile)


activation_complete = views.ActivationComplete.as_view()
registration_complete = views.RegistrationComplete.as_view()
registration_closed = views.RegistrationClosed.as_view()


class Register(views.Register):
    model_class = RegistrationProfile

    def get_notification_kwargs(self):
        return {'site': RequestSite(self.request)}
register = Register.as_view()
register_with_notification = Register.as_view(
    model_class=NotifyRegistrationProfile,
)
register_but_closed = Register.as_view(registration_closed=True)


class Activate(views.Activate):
    model_class = RegistrationProfile

    def activate(self):
        self.profile.user.is_active = True
        self.profile.user.save()
        self.profile.activation_key = self.profile.ACTIVATED
        self.profile.save()
activate = Activate.as_view()
activate_expired = Activate.as_view(model_class=ExpiringRegistrationProfile)
