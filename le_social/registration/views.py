from django.conf import settings
from django.contrib.sites.requests import RequestSite
from django.core import signing
from django.core.mail import send_mail
try:
    from django.urls import reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.views import generic

from ..utils import get_user_model
from .forms import RegistrationForm


class ActivationComplete(generic.TemplateView):
    template_name = 'le_social/registration/activation_complete.html'


class Activate(generic.TemplateView):
    template_name = 'le_social/registration/activate.html'
    success_url = reverse_lazy('registration_activation_complete')
    expires_in = 60 * 60 * 24 * 30  # 30 days

    def dispatch(self, request, *args, **kwargs):
        try:
            self.activation_key = signing.loads(kwargs['activation_key'],
                                                max_age=self.get_expires_in(),
                                                salt='le_social.registration')
        except signing.BadSignature:
            return super(Activate, self).dispatch(request, *args, **kwargs)
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.activate()
        return redirect(self.get_success_url())

    def get_expires_in(self):
        return self.expires_in

    def get_success_url(self):
        return force_text(self.success_url)

    def activate(self):
        get_user_model().objects.filter(
            pk=self.activation_key).update(is_active=True)


class Register(generic.FormView):
    closed_url = reverse_lazy('registration_closed')
    form_class = RegistrationForm
    registration_closed = False
    success_url = reverse_lazy('registration_complete')
    template_name = 'le_social/registration/register.html'
    notification_template_name = 'le_social/registration/activation_email.txt'
    notification_subject_template_name = ('le_social/registration/'
                                          'activation_email_subject.txt')

    def dispatch(self, request, *args, **kwargs):
        if self.get_registration_closed():
            return redirect(self.get_closed_url())
        return super(Register, self).dispatch(request, *args, **kwargs)

    def get_registration_closed(self):
        return self.registration_closed

    def get_closed_url(self):
        return force_text(self.closed_url)

    def form_valid(self, form):
        self.user = form.save()
        self.activation_key = signing.dumps(self.user.pk,
                                            salt='le_social.registration')
        self.send_notification()
        return super(Register, self).form_valid(form)

    def get_notification_context(self):
        return {
            'user': self.user,
            'activation_key': self.activation_key,
            'site': RequestSite(self.request),
        }

    def send_notification(self):
        context = self.get_notification_context()
        send_mail(
            render_to_string(self.notification_subject_template_name,
                             context).strip(),
            render_to_string(self.notification_template_name, context),
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
        )


class RegistrationComplete(generic.TemplateView):
    template_name = 'le_social/registration/registration_complete.html'


class RegistrationClosed(generic.TemplateView):
    template_name = 'le_social/registration/registration_closed.html'
