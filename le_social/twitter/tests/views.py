from __future__ import absolute_import

import twitter

from django.http import HttpResponse

from .. import views

kwargs = {'consumer_key': 'key',
          'consumer_secret': 'secret'}

authorize = views.Authorize.as_view(**kwargs)


class Callback(views.Callback):
    def error(self, message, exception=None):
        return HttpResponse(message)

    def success(self, auth):
        api = twitter.Twitter(auth=auth)
        user = api.account.verify_credentials()
        return HttpResponse(user['screen_name'])
callback = Callback.as_view(**kwargs)
