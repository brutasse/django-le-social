OpenID authentication
=====================

Requirements
------------

Install the ``python-openid`` package::

    pip install python-openid

For OpenID support, you need ``le_social.openid`` in your ``INSTALLED_APPS``.
Make sure you run ``manage.py syncdb``.

If you want to access the list of OpenID URLs associated to the current
session, add ``le_social.middleware.OpenIDMiddleware`` to your
``MIDDLEWARE_CLASSES``. This will add an ``openids`` attribute to incoming
requests. ``request.opendis`` is a list of ``le_social.openid.utils.OpenID``
objects.

Basic usage
-----------

Define the two URLs to initiate the OpenID connection and the return URL:

.. code-block:: python

    from myapp import views

    urlpatterns = patterns('',
        url(r'^openid/$', views.begin, name='openid_begin'),
        url(r'^openid/complete/$', views.callback, name='openid_complete'),
    )

And define your two view using the base classes provided by django-le-social:

.. code-block:: python

    from django.http import HttpResponse

    from le_social.openid import views

    class Begin(views.Begin):
        return_url = '/openid/complete/'
        template_name = 'openid.html'

        def failure(self, message):
            return HttpResponse(message)
    begin = Begin.as_view()

    class Callback(views.Callback):
        return_url = '/openid/complete/'

        def success(self):
            openid_url = self.openid_response.identity_url
            # self.openid_response contains the openid info
            return HttpResponse('Openid association: %s' % openid_url)

        def failure(self, message):
            return HttpResponse(message)
    callback = Callback.as_view()

You also need a basic template to render the OpenID form:

.. code-block:: html+django

    <form method="post" action=".">
        {{ form.as_p }}
        {% csrf_token %}
        <input type="submit" value="Sign in">
    </form>

This code will just return the OpenID URL in case of successful
authentication. Usually in the ``success()`` method, you would need to store
the OpenID URL in the DB, attach it to the currently logged-in user or create
a new user object.

The ``failure()`` methods are here to handle authentication failures, when the
OpenID URL isn't valid or something goes wrong during the OpenID negociation.

Extension points
----------------

Return URL
``````````

Both the ``Begin`` and ``Callback`` views need a ``return_url`` attribute. In
the examples above the URL is hardcoded but you can provide a
dynamically-generated one by defining ``get_return_url()`` on the view class
or on a mixin shared by your subclasses:

.. code-block:: python

    from django.core.urlresolvers import reverse

    from le_social.openid import views

    class ReturnUrlMixin(object):
        def get_return_url(self):
            return reverse('openid_complete')

    class Begin(ReturnUrlMixin, views.Begin):
        pass
    begin = Begin.as_view()

    class Callback(ReturnUrlMixin, views.Callback):
        def success(self):
            return something
    callback = Callback.as_view()

Form class
``````````

The ``Begin`` view is a standard ``FormView`` that takes a ``form_class``
attribute. The default value is ``le_social.openid.forms.OpenIDForm``, it just
asks for a valid URL. If you want to do more specific validation, subclass the
form and override ``clean_openid_url()``.

Sreg attributes
```````````````

The ``sreg_attrs`` dictionnnary on the ``Begin`` class defines which Sreg
fields to ask for. By default it is an empty dict but if you don't specify
anything it automatically gets updated to
``{'optional': ['nickname', 'email']}``.

You can alter the ``sreg_attrs`` attribute or implement ``get_sreg_attrs()``
on the view class.

Attribute Exchange
``````````````````

The ``ax_attrs`` attribute on the ``Begin`` class defines which AX attributes
to request. By default it is an empty list. If you need to set this
dynamically, implement ``get_ax_attrs()``.

Trust Root
``````````

By default the trust root is the root of your website. If you want to change
it, alter the ``trust_root`` attribute on the ``Begin`` class, or define
``get_trust_root()``. Note that ``trust_root`` must be a URL without the host
(e.g. ``'/something/'``), whereas ``get_trust_root()`` must return a full URL,
including the protocol and host name.

OpenID objects
--------------

With the ``OpenIDMiddleware``, the request gets an ``openids`` attribute, a
list of the OpenIDs associated to the current session. Each element is a
``le_social.openid.utils.OpenID`` instance and has the following information
attached:

* ``openid``: the OpenID URL
* ``issued``: the time when the association was successful
* ``attrs``: the OpenID attributes
* ``sreg``: the Sreg attributes
* ``ax``: the AX attributes.
