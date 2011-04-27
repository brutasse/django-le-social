from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views import generic

import tweepy


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
    def get(self, request, *args, **kwargs):
        auth = tweepy.OAuthHandler(self.get_consumer_key(),
                                   self.get_consumer_secret(), secure=True)
        url = auth.get_authorization_url(signin_with_twitter=True)
        request.session['request_token'] = (auth.request_token.key,
                                            auth.request_token.secret)
        return redirect(url)


class Return(generic.View, OAuthMixin):
    """
    A base class for the return callback. Subclasses must define:

        - error(error_msg, exception=None): what to do when
          something goes wrong? Must return an HttpResponse

        - success(auth): what to do on successful auth? Do
          some stuff with the tweepy.OAuth object and return
          an HttpResponse
    """
    def get(self, request, *args, **kwargs):
        verifier = request.GET.get('oauth_verifier', None)
        if verifier is None:
            return self.error('No verifier code')

        if not 'request_token' in request.session:
            return self.error('No request token found in the session')

        request_token = request.session.pop('request_token')
        request.session.modified = True

        auth = tweepy.OAuthHandler(self.get_consumer_key(),
                                   self.get_consumer_secret(), secure=True)
        auth.set_request_token(request_token[0], request_token[1])
        try:
            auth.get_access_token(verifier=verifier)
        except tweepy.TweepError as e:
            return self.error('Failed to get an access token')

        return self.success(auth)

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
