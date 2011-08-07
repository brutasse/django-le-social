from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect

from ..utils import generic, reverse_lazy

from .forms import RegistrationForm


class ActivationComplete(generic.TemplateView):
    template_name = 'le_social/registration/activation_complete.html'


class Activate(generic.TemplateView):
    model_class = None
    template_name = 'le_social/registration/activate.html'
    success_url = reverse_lazy('registration_activation_complete')

    def dispatch(self, request, *args, **kwargs):
        self.activation_key = kwargs['activation_key']
        if self.model_class is None:
            raise ImproperlyConfigured(
                "Provide a model class attribute that extends "
                "le_social.registration.models.RegistrationProfile"
            )
        try:
            self.profile = self.model_class.objects.get(
                activation_key=self.activation_key,
            )
        except self.model_class.DoesNotExist:
            return super(Activate, self).dispatch(request, *args, **kwargs)
        if self.profile.activation_key_expired():
            return super(Activate, self).dispatch(request, *args, **kwargs)

        self.activate()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.success_url

    def activate(self):
        raise NotImplementedError("Provide an implementation of activate()")


class Register(generic.FormView):
    closed_url = reverse_lazy('registration_closed')
    form_class = RegistrationForm
    model_class = None
    registration_closed = False
    success_url = reverse_lazy('registration_complete')
    template_name = 'le_social/registration/register.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_registration_closed():
            return redirect(self.get_closed_url())
        return super(Register, self).dispatch(request, *args, **kwargs)

    def get_registration_closed(self):
        return self.registration_closed

    def get_closed_url(self):
        return self.closed_url

    def get_model_class(self):
        return self.model_class

    def get_notification_kwargs(self):
        """
        The **kwargs to send to the profile's send_notification() method.
        Useful to pass a site or a request object for instance.
        """
        return {}

    def form_valid(self, form):
        self.profile = form.save()
        self.profile.send_notification(**self.get_notification_kwargs())
        return super(Register, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(Register, self).get_form_kwargs()
        kwargs.update({
            'model_class': self.get_model_class()
        })
        return kwargs


class RegistrationComplete(generic.TemplateView):
    template_name = 'le_social/registration/registration_complete.html'


class RegistrationClosed(generic.TemplateView):
    template_name = 'le_social/registration/registration_closed.html'
