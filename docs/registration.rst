Traditional Registration
========================

.. note:: Django versions

    Django-le-social 0.6 requires Django 1.4 or greater. If you still run
    Django <= 1.3, use django-le-social==0.5.

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

* The URLs.

* If you need something different than the default scenario, an
  implementation of the registration and activation logic.

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

Add some URLs in ``registration/urls.py``:

.. code-block:: python

    from django.conf.urls import patterns, url

    from . import views

    urlpatterns = patterns('',
        url(r'^activate/complete/$', views.activation_complete,
            name='registration_activation_complete'),

        url(r'^activate/(?P<activation_key>[^/]+)/$', views.activate,
            name='registration_activate'),

        url(r'^register/$', views.register,
            name='registration_register'),

        url(r'^register/complete/$', views.registration_complete,
            name='registration_complete'),

        url(r'^register/closed/$', views.registration_closed,
            name='registration_closed'),
    )


Finally, add the ``registration.views`` you referenced in ``urls.py``. In this
example, we'll be using the default behaviour that creates an inactive Django
user on registration, sends him a verification email and activates his account
when he clicks on the activation link.

.. code-block:: python

    from le_social.registration import views

    register = views.Register.as_view()
    registration_complete = views.RegistrationComplete.as_view()
    registration_closed = views.RegistrationClosed.as_view()

    activate = views.Activate.as_view()
    activation_complete = views.ActivationComplete.as_view()

Extension points
----------------

Registration form
`````````````````

``le_social.registration.views.Register`` is a `FormView`_. The default
registration form asks for:

* A username

* An email address

* Two passords

The default form only checks that the email is correct and the two passwords
match. If you want to perform extra validation, such as checking that the
username and the email are unique, just subclass the form and add your
validation logic:

.. _FormView: https://docs.djangoproject.com/en/dev/ref/class-based-views/generic-editing/#formview

.. code-block:: python

    from django import forms
    from le_social.registration.forms import RegistrationForm

    class MyRegistrationForm(RegistrationForm):
        def clean_username(self):
            if User.objects.filter(
                username=self.cleaned_data['username'],
            ).exists():
                raise forms.ValidationError('This username is already being used')
            return self.cleaned_data['username']

Then declare your custom form in the ``Register`` view. Instead of doing:

.. code-block:: python

    register = views.Register.as_view()

Do:

.. code-block:: python

    from .forms import MyRegistrationForm

    register = views.Register.as_view(
        form_class=MyRegistrationForm,
    )

Or even:

.. code-block:: python

    from .forms import MyRegistrationForm

    class Register(views.Register):
        form_class = MyRegistrationForm
    register = Register.as_view()

You can also completely rewrite the registration form to ask for different
fields. However, there are a couple of requirements for this form:

* It **must** implement a ``save()`` method. The default form's ``save()``
  implementation inserts a new ``User`` object from ``django.contrib.auth``.
  If you need a custom user model, define ``save()`` on your form to create a
  different object.

* The ``save()`` method **must** return a ``User`` object, or any model
  instance that has a primary key. This object is added to the template
  context for the registration notification (see below) and the primary key is
  used to generate the activation link.

Registration notification
`````````````````````````

The ``Register`` view has a ``send_notification()`` method that sends an
activation email by default. The following templates are used:

* ``le_social/registration/activation_email.txt`` for the email body,

* ``le_social/registration/activation_email_subject.txt`` for the email
  subject.

The following context variables are available:

* ``user``: the ``User`` instance returned by your form's ``save()`` method.

* ``site``: a ``RequestSite`` object from the current request.

* ``activation_key``: the signed key to put in your activation link. You can
  build the activation link like this:

  .. code-block:: jinja

      http://{{ site.domain }}{% url "registration_activate" activation_key %}

If you need more context variables, override ``get_notification_context()`` on
the ``Register`` view. For instance, to add a ``scheme`` variable containing
either ``http`` or ``https``:

.. code-block:: python

    class Register(views.Register):
        def get_notification_context(self):
            context = super(Register, self).get_notification_context()
            context.update({
                'scheme': 'https' if self.request.is_secure() else 'http'
            })
            return context

Other registration parameters
`````````````````````````````

The following attributes of the ``Register`` class can be customized:

* ``closed_url``: the URL to redirect to if the registration is closed.
  Defaults to ``reverse('registration_closed')``.

* ``form_class``: the form to use for registration. Defaults to
  ``le_social.registation.forms.RegistrationForm``.

* ``registration_closed``: boolean to open or close the registration. Defaults
  to ``False``.

* ``success_url``: the URL to redirect to on successful registration. Defaults
  to ``reverse('registration_complete')``.

* ``template_name``: the template to use to render the registration form.
  Defaults to ``'le_social/registration/register.html'``.

* ``notification_template_name``: the template to use for the notification
  email. Defaults to ``'le_social/registration/activation_email.txt'``.

* ``notification_subject_template_name``: the template to use for the
  notification subject. Defaults to
  ``'le_social/registration/activation_email_subject.txt'``.

The following methods can be customized:

* ``get_registration_closed()``: returns the value of ``registration_closed``.

* ``get_closed_url()``: returns the value of ``closed_url``.

* ``get_notification_context()``: builds the template context for the
  activation email.

* ``send_notification()``: sends the activation notification. This is an email
  by default, but you can override this method to do anything else instead.

Activation view
```````````````

The ``Activate`` view is a simple ``TemplateView`` that loads the activation
key into an ``activation_key`` attribute.

The key is signed using your ``SECRET_KEY`` setting. If the key is properly
loaded, the activation view calls the ``activate()`` method and redirects to a
``get_success_url()``.

If the key is not valid, the template is rendered. Hence the template should
show a "unable to activate" message, or something similar.

The following attributes can be set on the ``Activate`` view:

* ``template_name``: the template to use in case of failed activation.
  Defaults to ``'le_social/registration/activate.html'``.

* ``success_url``: the URL to redirect to in case of successful activation.
  Defaults to ``reverse('registration_activation_complete')``.

* ``expires_in``: the delay (in seconds) after which an activation link should
  be considered as expired. Defaults to ``2592000`` (30 days), set it to
  ``None`` if you want them to never expire.

The following methods can be overriden:

* ``get_expires_in()``: returns the content of ``expires_in`` by default.

* ``get_success_url()``: returns the content of ``success_url``.

* ``activate()``: sets the user's ``is_active`` attribute to ``True``. Override it if you have a custom user model.

Other registration views
------------------------

The other views are plain ``TemplateViews``, their templates are not provided
either. Here are the default paths, which you can alter using
``template_name``.

* ``RegistrationComplete``: renders
  ``le_social/registration/registration_complete.html``.

* ``RegistrationClosed``: renders
  ``le_social/registration/registration_closed.html``.

* ``ActivationComplete``: renders
  ``le_social/registration/activation_complete.html``.
