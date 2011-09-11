from __future__ import absolute_import

import twitter
from twitter import oauth_dance

from django.core.urlresolvers import reverse
from django.test import TestCase


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
    urls = 'le_social.twitter.tests.urls'

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
