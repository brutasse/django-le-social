Django-le-social
================

Django-le-social is an external registration helper for Django. It currently
lets you use Twitter (OAuth) and OpenID authentication.

It's more a framework than a drop-in app in the sense that it won't create
any user data for you: when a user comes from an external authentication
source, django-le-social executes a method that **you** decide. There is no
user creation, no new model instance, no user login. You need to decide what
to do, mainly store the OAuth token or the OpenID data and log the user in.

The source code is `available on Github`_ under the 3-clause BSD licence.

.. _available on Github: https://github.com/brutasse/django-le-social

Installation
------------

Django-le-social is Django >= 1.3 only since it's mainly class-based views.

::

    pip install django-le-social

Usage
-----

.. toctree::
   :maxdepth: 2

   twitter
   openid

Changes
-------

* 0.2:

  * renamed OpenID's and Twitter's ``Return`` views to ``Callback``
  * added ``build_callback`` for custom twitter callback URLs

* 0.1: initial version

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

