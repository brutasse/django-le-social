from django.contrib.auth.models import User
from django.core import mail
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import TestCase


class RegistrationTest(TestCase):
    valid_data = {
        'username': 'brutasse',
        'email': 'foo@example.com',
        'password1': 'foo',
        'password2': 'foo',
    }

    def test_static_pages(self):
        """Static registration-related pages"""
        for name in ('activation_complete', 'complete', 'closed'):
            url = reverse('registration_%s' % name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_register(self):
        self.assertEqual(User.objects.count(), 0)
        url = reverse('registration_register')
        response = self.client.get(url)
        self.assertContains(response, '<form ')
        data = {
            'username': '")*(@@!!',
            'email': 'yo dawg',
            'password1': 'foo',
            'password2': 'bar',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username',
                             'The username must contain only letters, numbers '
                             'and underscores.')
        try:
            self.assertFormError(response, 'form', 'email',
                                 'Enter a valid email address.')
        except AssertionError:
            self.assertFormError(response, 'form', 'email',
                                 'Enter a valid e-mail address.')
        self.assertFormError(response, 'form', None,
                             "The two passwords didn't match.")
        response = self.client.post(url, self.valid_data, follow=True)
        self.assertContains(response, "Registration complete")
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(User.objects.count(), 1)

    def test_strip_subject_line(self):
        url = reverse('registration_register')
        response = self.client.post(url, {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'foo',
            'password2': 'foo',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        # This raises BadHeaderError if header is not properly stripped
        mail.outbox[0].message()

    def test_register_with_no_notification(self):
        url = reverse('registration_register_with_notification')
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(url, self.valid_data, follow=True)
        self.assertContains(response, "Registration complete")
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_activate(self):
        url = reverse('registration_register')
        response = self.client.post(url, self.valid_data)

        self.assertFalse(User.objects.get().is_active)
        url = mail.outbox[0].body.split('testserver')[1].split('\n')[0]
        response = self.client.get(url, follow=True)
        self.assertContains(response, "Account successfully activated")
        self.assertEqual(len(response.redirect_chain), 1)

    def test_closed_registration(self):
        url = reverse('registration_register_but_closed')
        response = self.client.get(url, follow=True)
        self.assertContains(response, "Registration is closed")
        self.assertEqual(len(response.redirect_chain), 1)

    def test_activation_key_expired(self):
        """
        Registration has expired
        """
        url = reverse('registration_register_expired')
        response = self.client.post(url, self.valid_data)
        url = mail.outbox[0].body.split('testserver')[1].split('\n')[0]
        response = self.client.get(url)
        self.assertContains(response, 'Invalid')
