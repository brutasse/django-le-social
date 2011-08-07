import twitter
from twitter import oauth_dance

from openid.consumer import consumer
from openid.message import Message

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import RegistrationProfile
from ..openid import utils


def discover_extensions(openid_url):
    """
    Don't bother with extensions for tests.
    """
    return False, False


class OpenidRequest(object):
    """
    Fake OpenID request
    """
    def __init__(self, url):
        self.url = url

    def addExtension(self, sreg_request):
        pass

    def redirectURL(self, trust_root, return_url):
        return trust_root[:-1] + return_url


class OpenidResponse(object):
    """
    Fake OpenID response
    """
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.identity_url = 'http://bruno.renie.fr'
        self.signed_fields = None

    def getSignedNS(self, uri):
        return self.message.getArgs(uri)

    def extensionResponse(self, namespace_uri, require_signed):
        if require_signed:
            return self.getSignedNS(namespace_uri)
        else:
            return self.message.getArgs(namespace_uri)


class Consumer(object):
    """
    Fake OpenID consumer
    """
    def __init__(self, session, store_class):
        self.session = session
        self.store_class = store_class

    def begin(self, url):
        return OpenidRequest(url)

    def complete(self, query, return_url):
        if not query:
            return OpenidResponse(consumer.FAILURE, 'Invalid openid.mode')
        return OpenidResponse(consumer.SUCCESS, Message())


class OpenidTest(TestCase):
    urls = 'le_social.tests.openid_urls'

    def setUp(self):
        self._real_consumer = consumer.Consumer
        consumer.Consumer = Consumer

        self._real_discover_extensions = utils.discover_extensions
        utils.discover_extensions = discover_extensions

    def tearDown(self):
        consumer.Consumer = self._real_consumer
        utils.discover_extensions = self._real_discover_extensions

    def test_openid_assoc(self):
        url = reverse('openid_begin')
        response = self.client.get(url)
        self.assertContains(response, '<form ')
        data = {'openid_url': 'http://bruno.renie.fr'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_failed_callback(self):
        url = reverse('openid_callback')
        response = self.client.get(url)
        self.assertContains(response, 'Invalid openid.mode')

    def test_successful_callback(self):
        url = reverse('openid_callback') + '?type=success'
        response = self.client.get(url)
        self.assertContains(response, 'OpenID association')


def parse_oauth_tokens(tokens):
    return tokens


class OAuth(object):
    def request_token(self, oauth_callback):
        return 'token', 'token_secret'

    def access_token(self, oauth_verifier):
        return 'Yay', 'access token'


class Account(object):
    def verify_credentials(self):
        return {'screen_name': 'brutasse'}


class Twitter(object):
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.oauth = OAuth()
        self.account = Account()


class TwitterTest(TestCase):
    urls = 'le_social.tests.twitter_urls'

    def setUp(self):
        self._old_twitter = twitter.Twitter
        twitter.Twitter = Twitter

        self._old_parse_tokens = oauth_dance.parse_oauth_tokens
        oauth_dance.parse_oauth_tokens = parse_oauth_tokens

    def tearDown(self):
        twitter.Twitter = self._old_twitter
        oauth_dance.parse_oauth_tokens = self._old_parse_tokens

    def test_authorize(self):
        url = reverse('authorize')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_callback(self):
        url = reverse('callback')
        response = self.client.get(url)
        self.assertContains(response, "No verifier code")

        url += '?oauth_verifier=foobar'
        response = self.client.get(url)
        self.assertContains(response, "No request token found in the session")

        self.client.get(reverse('authorize'))
        response = self.client.get(url)
        self.assertContains(response, 'brutasse')


class RegistrationTest(TestCase):
    urls = 'le_social.tests.registration_urls'
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
        self.assertEqual(RegistrationProfile.objects.count(), 0)
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
        self.assertFormError(response, 'form', 'email',
                             'Enter a valid e-mail address.')
        self.assertFormError(response, 'form', None,
                             "The two passwords didn't match.")
        response = self.client.post(url, self.valid_data, follow=True)
        self.assertContains(response, "Registration complete")
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(len(mail.outbox), 0)  # No notification in this case
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(RegistrationProfile.objects.count(), 1)

    def test_register_with_notification(self):
        url = reverse('registration_register_with_notification')
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(url, self.valid_data, follow=True)
        self.assertContains(response, "Registration complete")
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_activate(self):
        url = reverse('registration_register')
        response = self.client.post(url, self.valid_data)

        profile = RegistrationProfile.objects.get()
        self.assertFalse(User.objects.get().is_active)
        url = reverse('registration_activate', args=[profile.activation_key])
        response = self.client.get(url, follow=True)
        self.assertContains(response, "Account successfully activated")
        self.assertEqual(len(response.redirect_chain), 1)

        response = self.client.get(url)
        self.assertContains(response, "Invalid")

    def test_closed_registration(self):
        url = reverse('registration_register_but_closed')
        response = self.client.get(url, follow=True)
        self.assertContains(response, "Registration is closed")
        self.assertEqual(len(response.redirect_chain), 1)

    def test_activation_key_expired(self):
        url = reverse('registration_register')
        response = self.client.post(url, self.valid_data)

        profile = RegistrationProfile.objects.get()
        url = reverse('registration_activate_expired',
                      args=[profile.activation_key])
        response = self.client.get(url)
        self.assertContains(response, 'Invalid')
