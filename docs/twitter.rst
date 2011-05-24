Twitter authentication
======================

Basic usage
-----------

Communications with Twitter are handled with tweepy. Define two URLs, one to
initiate the twitter login and the other for the OAuth callback:

.. code-block:: python

    from myapp import views

    urlpatterns = patterns('',
        url(r'^oauth/authorize/$', views.authorize, name='oauth_authorize'),
        url(r'^oauth/callback/$', views.callback, name='oauth_callback'),
    )

Set your OAuth consumer key and secret in your settings:

.. code-block:: python

    CONSUMER_KEY = 'yayyaaa'
    CONSUMER_SECRET = 'whoooooohooo'

And create the two views:

.. code-block:: python

    from django.http import HttpResponse
    from django.shortcuts import redirect
    from django.utils import simplejson as json

    import tweepy

    from le_social.twitter import views

    authorize = views.Authorize.as_view()

    class Callback(views.Callback):
        def error(self, message, exception=None):
            return HttpResponse(message)

        def success(self, auth):
            api = tweepy.API(auth, parser=RawParser())
            response = api.me()
            user, created = SomeModel.objects.get_or_create(
                screen_name=json.loads(response)['screen_name']
            )
            user.key = auth.access_token.key
            user.secret = auth.access_token.secret
            user.save()
            return redirect(reverse('some_view'))
    callback = Callback.as_view()

On the ``Callback`` view, you need to implement the
``error(message, exception=None)`` and ``success(auth)`` methods.
Both must return an HTTP response.

Extension points
----------------

Authorize
`````````

The ``Authorize`` is a ``django.views.generic.View`` subclass. Customization
can be done using the extension points it provides. For instance, if one
doesn't want to allow logged-in users to sign in with Twitter:

.. code-block:: python

    class Authorize(views.Authorize):
        def get(self, request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect('/')
            return super(Authorize, self).get(request, *args, **kwargs)
    authorize = Authorize.as_view()

Callback
````````

You can also special-case the ``Callback`` view using the same technique, but
you really need to implement the ``error()`` and ``success()`` methods on this
class.

OAuth credentials
`````````````````

By default, the ``Authorize`` and ``Callback`` views look for the Twitter app
credentials in your settings (``CONSUMER_KEY``, ``CONSUMER_SECRET``). You can
implement your own mixin instead. The default OAuth mixin looks for the
consumer key and secrets in this order:

* ``consumer_key`` and ``consumer_secret`` as attributes on the view class,
* ``settings.CONSUMER_KEY`` and ``settings.CONSUMER_SECRET``

If you set ``consumer_key`` and ``consumer_secret`` on the class, you need to
do so on the two views, or make your custom views inherit from a mixin that
provides them.

For more logic, you can also re-implement ``get_consumer_key()`` and
``get_consumer_secret()`` on the view classes to use different consumers under
certain conditions:

.. code-block:: python

    class OAuthMixin(views.OAuthMixin):
        def get_consumer_key(self):
            if self.request.user.username == 'bruno':
                return 'hahahah'
            return super(OAuthMixin, self).get_consumer_key()

    class Authorize(OAuthMixin, views.Authorize):
        pass
    authorize = Authorize.as_view()

    class Callback(OAuthMixin, views.Callback):
        def success(self, auth):
            do_some_stuff()
            return something
    callback = Callback.as_view()
