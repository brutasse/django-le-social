from .. import views

activation_complete = views.ActivationComplete.as_view()
registration_complete = views.RegistrationComplete.as_view()
registration_closed = views.RegistrationClosed.as_view()
register = views.Register.as_view()


class NoNotificationRegistration(views.Register):
    def send_notification(self):
        return
register_with_no_notification = NoNotificationRegistration.as_view()

register_but_closed = views.Register.as_view(registration_closed=True)
activate = views.Activate.as_view()


register_expired = views.Register.as_view(
    notification_template_name=('le_social/registration/'
                                'expired_activation_email.txt'),
)


class ExpiringActivate(views.Activate):
    expires_in = -1  # In the past
activate_expired = ExpiringActivate.as_view()
