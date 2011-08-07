Traditional Registration
========================

This part explains how to use le-social to handle *traditional* registration,
ala `django-registration`_.

.. _django-registration: http://pypi.python.org/pypi/django-registration

Here's the workflow:

* A user visits your site
* He clicks "register"
* He fills a form asking him for some details
* He gets a notification (email, SMS, postcard, rocket) with a secret
  activation link
* He follows the link and his account is activated

You need to add to your project:

* A model to store the registration profiles, with a ForeignKey to your User
  model (usually the User model from ``django.contrib.auth`` but it can be
  anything else).

* An implementation of the registration and activation logic.

* The URLs.

Everything you need is under the ``le_social.registration`` namespace.

Basic Usage
-----------

This example will show you how to implement the equivalent of
django-registration.


.. note:: Templates

    No templates are provided with django-le-social. See the end of this page
    for the default template paths.

First, create an app. Let's call it ``registration``:

.. code-block:: bash

    python manage.py startapp registration

Create a model in ``registration/models.py``, extending
``RegistrationProfile`` (which is an abstract model). We need to link it to
our user object, in this case Django's own ``User`` model. The class also
needs to implement a ``send_notification()`` method, which is used to send an
activation link to our user.

.. code-block:: python

    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.db import models
    from django.template import loader

    from le_social.registration import models as registration_models

    class RegistrationProfile(registration_models.RegistrationProfile):
        user = models.ForeignKey(User)

        def send_notification(self, **kwargs):
            context = {'profile': self,
                       'user': self.user,
                       'site': kwargs.pop('site')},
            send_mail('Account activation', loader.render_to_string(
                'le_social/registration/activation_email.txt', context,
            ), 'no-reply@example.com', [self.user.email])

``send_notification()`` can be used to send email or anything else. Since your
view code will call this method, you can make it accept any arguments, such as
a ``Site`` object in this case (useful for the activation link in the email
body).

Next, add some URLs:

.. code-block:: python

    from django.conf.urls.defaults import patterns, url

    from registration import views

    urlpatterns = patterns('',
        url(r'^activate/complete/$', views.activation_complete,
            name='registration_activation_complete'),

        url(r'^activate/(?P<activation_key>\w+)/$', views.activate,
            name='registration_activate'),

        url(r'^register/$', views.register,
            name='registration_register'),

        url(r'^register/complete/$', views.registration_complete,
            name='registration_complete'),

        url(r'^register/closed/$', views.registration_closed,
            name='registration_closed'),
    )


Finally, add the ``registration.views`` you referenced in ``urls.py``. In this
example, we'll be creating an inactive Django user on registration, send him
a verification email and activate his account when he clicks on the activation
link

.. code-block:: python

    from django.contrib.sites.models import RequestSite

    from le_social.registration import views

    from registration.models import RegistrationProfile

    activation_complete = views.ActivationComplete.as_view()
    registration_complete = views.RegistrationComplete.as_view()
    registration_closed = views.RegistrationClosed.as_view()

    class Register(views.Register):
        model_class = RegistrationProfile

        def get_notification_kwargs(self):
            return {'site': RequestSite(self.request)}
    register = Register.as_view()

    class Activate(views.Activate):
        model_class = RegistrationProfile

        def activate(self):
            self.profile.user.is_active = True
            self.profile.user.save()
            self.profile.activation_key = self.profile.ACTIVATED
            self.profile.save()
    activate = Activate.as_view()

Extension points
----------------

The registration profile
````````````````````````

The registration profile, located at
``le_social.registration.models.RegistrationProfile``, implements the minimal
features required for registration:

* an ``activation_key`` field, for storing the activation key

* an ``activation_key_expired()`` method, to determine whether the activation
  key has expired or not. Keys never expire by default, you can customize the
  behaviour in a custom class. For instance, if you want keys to expire after
  30 days:

  .. code-block:: python

      class ExpiringRegistrationProfile(RegistrationProfile):
          user = models.ForeignKey(User)

          def activation_key_expired(self):
              delay = datetime.timedelta(days=30)
              now = datetime.datetime.now()
              return self.user.date_joined + delay < now

* a ``send_notification()`` method to send the activation link to the user.
  You can pass it any ``kwargs`` you want from your view code, which is useful
  for getting a ``site`` or ``request`` object.

  To generate the activation link, pass a ``site`` object and the activation
  key to a template:

  .. code-block:: jinja

      {% load url from future %}
      http://{{ site.domain }}{% url "registration_activate" activation_key %}

Registering your registration profile is done by attaching it to your
``Register`` and ``Activate`` views:

.. code-block:: python

    from le_social.registration import views

    class Register(views.Register):
        model_class = CustomRegistrationProfile

    class Activate(views.Activate):
        model_class = CustomRegistrationProfile

You can also have a common mixin for the two views. If you want to use
different profiles according to a certain logic, use ``get_model_class()``:

.. code-block:: python

    class RegistrationMixin(object):
        def get_model_class(self):
            if some_condition():
                return EmailRegistrationProfile
            return SMSRegistrationProfile

The registration form
`````````````````````

The default registration form asks for a username, an email address and a
password. It doesn't check for username or email uniqueness, so you probably
want to implement that depending on your requirements.

A registration form needs to implement two methods:

* ``save()``: this method creates an inactive user and a registration profile.
  If you write a custom form, have a look at
  ``le_social.registration.forms.RegistrationForm.save()``.

* ``get_derived_field()``: this method should return a string, unique for the
  user you're registering: a username, an email address… This string, after
  being salted and hashed, is what generates the activation link. For
  instance, for the default registration form:

  .. code-block:: python

      def get_derived_field(self):
          return self.cleaned_data['username']

Register your custom registration form using ``form_class`` or
``get_form_class()``:

.. code-block:: python

    class Register(views.Register):
        form_class = CustomRegistrationForm

    # Or…

    class Register(views.Register):
        def get_form_class(self):
            if special_condition:
                return CustomRegistrationForm
            return RegistrationForm

The form class's ``__init__()`` method also needs to accept a ``model_class``
keyword argument.

The registration views
``````````````````````

Register
~~~~~~~~

``Register`` is a ``FormView``. A ``model_class`` is the only required
attribute (or its ``get_model_class()`` method counterpart). For further
customization, you can set:

* ``form_class``: as seen above, the form to use for registration.

* ``get_form_class()``: a method that returns the form class to use.

* ``registration_closed``: a boolean that determines whether the registration
  is closed or not.

* ``get_registration_closed()``: a method returning a boolean, the current
  status of registration

* ``closed_url``: the URL to redirect to if the registration is closed.

* ``get_closed_url()``: a method returning the redirect URL when registration
  is closed.

* ``success_url``: the URL to redirect to on successful registration.

* ``get_success_url()``: a method returning the redirect URL on successful
  registration.

* ``get_notification_kwargs()``: a method that returns the keyword arguments
  to be passed to the registration profile's ``send_notification()`` method.

On top of that, all the standard attributes / methods for a ``FormView``
are applicable.

Its default template (not provided) is set to
``le_social/registration/register.html``.

Activate
~~~~~~~~

``Activate`` is a ``TemplateView`` that redirects if the activation key is
matched. Its template should then display an error message telling the user
his request wasn't matched.

You need to implement ``activate()`` on this class. Other than that, you can
customize the redirection URL using ``success_url`` or ``get_success_url()``.

Its default template (not provided) is set to
``le_social/registration/activate.html``.

Other views
~~~~~~~~~~~

The other views are plain ``TemplateViews``, their templates are not provided
either. Here are the default paths, which you can alter using
``template_name``.

* ``RegistrationComplete``: renders
  ``le_social/registration/registration_complete.html``.

* ``RegistrationClosed``: renders
  ``le_social/registration/registration_closed.html``.

* ``ActivationComplete``: renders
  ``le_social/registration/activation_complete.html``.
