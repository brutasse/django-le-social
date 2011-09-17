Django-le-social
================

Django-le-social is an external registration helper for Django. It currently
lets you use Twitter (OAuth) and OpenID authentication, as well as traditional
registration.

Design
------

It's more a framework than a drop-in app in the sense that it won't create
any user data for you: when a user comes from an external authentication
source, django-le-social executes a method that **you** decide. There is no
user creation, no new model instance, no user login. You need to decide what
to do, mainly store the OAuth token or the OpenID data, create a user and log
him in.

The model structure is completely up to you: you can use django-le-social with
any user model or session backend, you should be able to plug it to almost any
existing project. If you can't, it's probably a bug -- please report back!

Django-le-social **doesn't add any settings**. While you can store some stuff
in the settings, it's not enforced. For application logic, we try to use
attributes and methods as much as possible.

Code
----

The source code is `available on Github`_ under the 3-clause BSD licence.

.. _available on Github: https://github.com/brutasse/django-le-social

Installation
------------

Django-le-social is mainly class-based views. It's been written for Django
1.3 but compatibility with older versions is provided using the `django-cbv`_
package.

.. _django-cbv: http://pypi.python.org/pypi/django-cbv

If you have Django >= 1.3:

::

    pip install django-le-social

If you have Django < 1.3:

::

    pip install django-le-social django-cbv

Django-le-social is tested for python 2.6, 2.7 and Django 1.2, 1.3 and trunk.

Usage
-----

.. toctree::
   :maxdepth: 2

   twitter
   openid
   registration

Changes
-------

* 0.4:

  * Test suite
  * Django < 1.3 compatibility with django-cbv
  * "Traditional" registration support, ala django-registration

* 0.3:

  * switched from tweepy to twitter for Twitter authentication
  * added the ability to force the login on the twitter authorization screen

* 0.2:

  * renamed OpenID's and Twitter's ``Return`` views to ``Callback``
  * added ``build_callback`` for custom twitter callback URLs

* 0.1: initial version

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

