from django import forms
from django.utils.translation import ugettext_lazy as _

from ..utils import get_user_model


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

    def clean(self):
        data = self.cleaned_data
        if ('password1' in data and 'password2' in data):
            if data['password1'] != data['password2']:
                raise forms.ValidationError(
                    _("The two passwords didn't match."),
                )
        return self.cleaned_data

    def save(self):
        user = get_user_model().objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
        )
        user.is_active = False
        user.save()
        return user
