from __future__ import absolute_import

try:
    from unittest import skipIf
except ImportError:
    from django.utils.unittest import skipIf

try:
    import twitter.oauth_dance
except ImportError:
    twitter = None

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import patch


def parse_oauth_tokens(tokens):
    return tokens


def side_effect(tokens):
    yield tokens


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
    urls = 'le_social.twitter.tests.urls'

    def setUp(self):
        self._old_twitter = twitter.Twitter
        twitter.Twitter = Twitter

    def tearDown(self):
        twitter.Twitter = self._old_twitter

    @patch('twitter.oauth_dance.parse_oauth_tokens')
    def test_authorize(self, parse):
        parse.side_effect = side_effect()
        url = reverse('authorize')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    @patch('twitter.oauth_dance.parse_oauth_tokens')
    def test_callback(self, parse):
        parse.side_effect = side_effect()
        url = reverse('callback')
        response = self.client.get(url)
        self.assertContains(response, "No verifier code")

        url += '?oauth_verifier=foobar'
        response = self.client.get(url)
        self.assertContains(response, "No request token found in the session")

        self.client.get(reverse('authorize'))
        response = self.client.get(url)
        self.assertContains(response, 'brutasse')
TwitterTest = skipIf(twitter is None, "twitter not installed")(TwitterTest)
