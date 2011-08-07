from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ..utils import make_activation_key


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$', max_length=30, label=_('Username'),
        error_messages={'invalid': _('The username must contain only letters, '
                                     'numbers and underscores.')},
    )
    email = forms.EmailField(label=_('Email'))
    password1 = forms.CharField(label=_('Password'),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password (again)'),
                                widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.model_class = kwargs.pop('model_class')
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data
        if ('password1' in data and 'password2' in data):
            if data['password1'] != data['password2']:
                raise forms.ValidationError(
                    _("The two passwords didn't match."),
                )
        return self.cleaned_data

    def save(self):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
        )
        user.is_active = False
        user.save()

        profile = self.model_class.objects.create(
            user=user,
            activation_key=make_activation_key(self.get_derived_field()),
        )
        return profile

    def get_derived_field(self):
        return self.cleaned_data['username']
