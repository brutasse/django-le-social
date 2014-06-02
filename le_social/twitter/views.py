from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views import generic

try:
    from twitter import Twitter, OAuth, TwitterError
    from twitter.oauth_dance import parse_oauth_tokens
except ImportError:
    raise ImproperlyConfigured(
        "twitter<1.8 is required to use le_social.twitter."
    )


class OAuthMixin(object):
    consumer_key = None
    consumer_secret = None

    def get_consumer_key(self):
        if self.consumer_key is not None:
            return self.consumer_key
        if hasattr(settings, 'CONSUMER_KEY'):
            return settings.CONSUMER_KEY
        else:
            raise ImproperlyConfigured("Set settings.CONSUMER_KEY or the "
                                       "consumer_key attribute or "
                                       "implement get_consumer_key")

    def get_consumer_secret(self):
        if self.consumer_secret is not None:
            return self.consumer_secret
        if hasattr(settings, 'CONSUMER_SECRET'):
            return settings.CONSUMER_SECRET
        else:
            raise ImproperlyConfigured("Set settings.CONSUMER_SECRET or the "
                                       "consumer_secret attribute or "
                                       "implement get_consumer_secret")


class Authorize(generic.View, OAuthMixin):
    """
    A base class for the authorize view. Just sets the request token
    in the session and redirects to twitter.
    """
    def get(self, request, force_login=False, *args, **kwargs):
        callback = self.build_callback()
        oauth = OAuth('', '',
                      self.get_consumer_key(),
                      self.get_consumer_secret())
        api = Twitter(auth=oauth, secure=True, format='', api_version=None)
        (oauth.token, oauth.token_secret) = parse_oauth_tokens(
            api.oauth.request_token(oauth_callback=callback))
        request.session['request_token'] = (oauth.token, oauth.token_secret)
        url = ('https://api.twitter.com/oauth/authenticate?oauth_token='
               '%s' % oauth.token)
        if force_login:
            url += '&force_login=true'
        return redirect(url)

    def build_callback(self):
        """ Override this if you'd like to specify a callback URL"""
        return None


class Callback(generic.View, OAuthMixin):
    """
    A base class for the return callback. Subclasses must define:

        - error(error_msg, exception=None): what to do when
          something goes wrong? Must return an HttpResponse

        - success(auth): what to do on successful auth? Do
          some stuff with the twitter.OAuth object and return
          an HttpResponse
    """
    def get(self, request, *args, **kwargs):
        verifier = request.GET.get('oauth_verifier', None)
        if verifier is None:
            return self.error('No verifier code')

        if 'request_token' not in request.session:
            return self.error('No request token found in the session')

        request_token = request.session.pop('request_token')
        request.session.modified = True

        oauth = OAuth(request_token[0], request_token[1],
                      self.get_consumer_key(),
                      self.get_consumer_secret())
        api = Twitter(auth=oauth, secure=True, format='', api_version=None)
        try:
            (oauth.token, oauth.token_secret) = parse_oauth_tokens(
                api.oauth.access_token(oauth_verifier=verifier))
        except TwitterError:
            return self.error('Failed to get an access token')

        return self.success(oauth)

    def success(self, auth):
        """
        Twitter authentication successful, do some stuff with his key.
        """
        raise NotImplementedError("You need to provide an implementation of "
                                  "success(auth)")

    def error(self, message, exception=None):
        """
        Meh. Something broke.
        """
        raise NotImplementedError("You need to provide an implementation of "
                                  "error(message, exception=None)")
